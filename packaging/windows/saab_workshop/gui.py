"""Minimal Tkinter GUI for saab-workshop.exe.

Tkinter ships with the standard CPython Windows installer, so this stays
dependency-free. If Tkinter is unavailable in the build environment, the
GUI command reports that cleanly and the CLI remains fully usable.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from .extractor import sync_vendor
from .launcher import TOOL_REGISTRY, launch_tool, list_available_tools
from .logging_setup import get_logger

if TYPE_CHECKING:
    from .config import WorkshopConfig


def run_gui(config: WorkshopConfig) -> int:
    logger = get_logger()
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
    except ImportError:
        logger.error(
            "tkinter is not available in this Python build; "
            "use the CLI instead (saab-workshop --help)"
        )
        print("GUI unavailable: tkinter is not installed. Use the CLI commands instead.")
        return 1

    root = tk.Tk()
    root.title("Saab Workshop Launcher")
    root.geometry("560x420")

    status_var = tk.StringVar(value=f"Home: {config.home_dir}")

    tree = ttk.Treeview(root, columns=("path",), show="tree headings", height=14)
    tree.heading("#0", text="Category")
    tree.heading("path", text="Executable")
    tree.column("#0", width=180)
    tree.column("path", width=340)
    tree.pack(fill="both", expand=True, padx=8, pady=8)

    def refresh() -> None:
        tree.delete(*tree.get_children())
        tools = list_available_tools(config)
        for category, paths in sorted(tools.items()):
            label = TOOL_REGISTRY[category][0]
            if not paths:
                tree.insert("", "end", iid=category, text=label, values=("(not found)",))
            else:
                for i, path in enumerate(paths):
                    tree.insert(
                        "",
                        "end",
                        iid=f"{category}::{i}",
                        text=label if i == 0 else "",
                        values=(str(path),),
                    )
        status_var.set(f"Home: {config.home_dir}  |  refreshed")

    def on_extract() -> None:
        source = filedialog.askdirectory(title="Select your local vendor source folder")
        if not source:
            return
        result = sync_vendor(config, Path(source))
        messagebox.showinfo(
            "Extract complete",
            f"copied={result.copied} unchanged={result.skipped_unchanged} "
            f"failed={result.failed} unclassified={result.skipped_unclassified}",
        )
        refresh()

    def on_launch() -> None:
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("No selection", "Select a tool to launch first.")
            return
        iid = selection[0]
        if "::" not in iid:
            messagebox.showwarning("Not found", "That category has no discovered executable.")
            return
        category, index_str = iid.split("::", 1)
        result = launch_tool(config, category, index=int(index_str))
        if result.ok:
            messagebox.showinfo("Launched", result.message)
        else:
            messagebox.showerror("Could not launch", result.message)

    button_bar = tk.Frame(root)
    button_bar.pack(fill="x", padx=8, pady=(0, 8))
    tk.Button(button_bar, text="Extract from folder...", command=on_extract).pack(side="left")
    tk.Button(button_bar, text="Refresh", command=refresh).pack(side="left", padx=6)
    tk.Button(button_bar, text="Launch selected", command=on_launch).pack(side="left")
    tk.Button(button_bar, text="Quit", command=root.destroy).pack(side="right")

    tk.Label(root, textvariable=status_var, anchor="w").pack(fill="x", padx=8, pady=(0, 8))

    refresh()
    root.mainloop()
    return 0
