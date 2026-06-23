import cv2
import traceback

backends = [
    (cv2.CAP_DSHOW, 'CAP_DSHOW'),
    (cv2.CAP_MSMF, 'CAP_MSMF'),
    (cv2.CAP_VFW, 'CAP_VFW'),
    (cv2.CAP_FFMPEG, 'CAP_FFMPEG'),
    (0, 'DEFAULT')
]

for idx in range(0, 4):
    print(f"\n--- Trying device index {idx} ---")
    for b, name in backends:
        try:
            print(f"Backend: {name} ({b})", end=' -> ')
            cap = cv2.VideoCapture(idx, b) if name != 'DEFAULT' else cv2.VideoCapture(idx)
            opened = cap.isOpened()
            print('opened=' + str(opened))
            if not opened:
                cap.release()
                continue
            ret, frame = cap.read()
            print('read_ret=' + str(ret))
            if ret and frame is not None:
                print('frame_shape=' + str(frame.shape))
            cap.release()
        except Exception:
            traceback.print_exc()

print('\nTest complete')
