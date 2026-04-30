#!/usr/bin/env python3
from __future__ import annotations

import argparse

import can
from can.remote import RemoteServer


def main():
    parser = argparse.ArgumentParser(description="SAAB Suite CAN remote gateway (Linux/RPi)")
    parser.add_argument("--channel", default="can0", help="SocketCAN interface (default: can0)")
    parser.add_argument("--bustype", default="socketcan", help="Bus type (default: socketcan)")
    parser.add_argument("--host", default="0.0.0.0", help="Listen host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=29536, help="Listen port (default: 29536)")
    args = parser.parse_args()

    bus = can.interface.Bus(channel=args.channel, bustype=args.bustype)
    server = RemoteServer(bus, (args.host, args.port))
    print(f"[GW] Listening on {args.host}:{args.port}, bus={args.bustype}:{args.channel}")
    server.serve_forever()


if __name__ == "__main__":
    main()
