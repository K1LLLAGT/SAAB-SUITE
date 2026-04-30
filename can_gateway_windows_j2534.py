from __future__ import annotations

import argparse

import can
from can.remote import RemoteServer


def main():
    parser = argparse.ArgumentParser(description="SAAB Suite CAN remote gateway (Windows J2534)")
    parser.add_argument("--channel", default="MongoosePro GM II", help="J2534 device name")
    parser.add_argument("--dll", required=True, help="Path to J2534 DLL")
    parser.add_argument("--host", default="0.0.0.0", help="Listen host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=29536, help="Listen port (default: 29536)")
    args = parser.parse_args()

    bus = can.interface.Bus(
        bustype="j2534",
        channel=args.channel,
        dll=args.dll,
    )
    server = RemoteServer(bus, (args.host, args.port))
    print(f"[GW] Listening on {args.host}:{args.port}, J2534={args.channel}")
    server.serve_forever()


if __name__ == "__main__":
    main()
