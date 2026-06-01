import socket, struct, time, os

OUT = r"C:\Users\mercu\clawd\incoming"
HFMT = "<IHHIIQ"
HSZ = struct.calcsize(HFMT)
frames = {}
saved = 0
DEADLINE = time.time() + 20.0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2.0)
sock.bind(("0.0.0.0", 5600))
print("listening on UDP 5600 ...")

try:
    while time.time() < DEADLINE and saved < 3:
        try:
            packet, addr = sock.recvfrom(65536)
        except socket.timeout:
            print("...no packets yet")
            continue
        if len(packet) < HSZ:
            continue
        frame_id, chunk_id, total_chunks, jpeg_size, payload_size, t_ns = struct.unpack(HFMT, packet[:HSZ])
        payload = packet[HSZ:]
        f = frames.setdefault(frame_id, {"chunks": {}, "total": total_chunks})
        f["chunks"][chunk_id] = payload
        if len(f["chunks"]) == f["total"]:
            ok = all(i in f["chunks"] for i in range(f["total"]))
            if ok:
                jpeg = bytearray()
                for i in range(f["total"]):
                    jpeg.extend(f["chunks"][i])
                p = os.path.join(OUT, "aigp_frame%d.jpg" % saved)
                open(p, "wb").write(bytes(jpeg))
                print("saved %s (%d bytes)" % (p, len(jpeg)))
                saved += 1
            del frames[frame_id]
finally:
    sock.close()
    print("done, saved=%d" % saved)
