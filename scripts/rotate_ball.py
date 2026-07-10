import sys
import os
import cv2
import numpy as np


def rotate_fill_only(input_path, output_path, clockwise=True):
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise SystemExit(f"Failed to open image: {input_path}")

    # Work in BGRA if available
    if img.shape[2] == 4:
        bgr = img[:, :, :3]
        alpha = img[:, :, 3]
    else:
        bgr = img
        alpha = None

    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    # Detect yellow ball region (tuned for bright yellow)
    lower_y = np.array([18, 60, 60])
    upper_y = np.array([40, 255, 255])
    mask_yellow = cv2.inRange(hsv, lower_y, upper_y)
    # Clean mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    mask_yellow = cv2.morphologyEx(mask_yellow, cv2.MORPH_CLOSE, kernel)
    mask_yellow = cv2.morphologyEx(mask_yellow, cv2.MORPH_OPEN, kernel)

    # Find largest contour assumed to be the ball
    contours, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise SystemExit("No yellow region found. Adjust thresholds.")

    c = max(contours, key=cv2.contourArea)
    (x, y), radius = cv2.minEnclosingCircle(c)
    x = int(x); y = int(y); radius = int(radius)

    h, w = bgr.shape[:2]
    ball_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(ball_mask, (x, y), radius, 255, -1)

    # Detect stitches (reddish color) to preserve them
    # Reddish/brown range (two ranges for red wrap)
    lower_r1 = np.array([0, 60, 40])
    upper_r1 = np.array([12, 255, 255])
    lower_r2 = np.array([160, 60, 40])
    upper_r2 = np.array([180, 255, 255])
    mask_r1 = cv2.inRange(hsv, lower_r1, upper_r1)
    mask_r2 = cv2.inRange(hsv, lower_r2, upper_r2)
    mask_red = cv2.bitwise_or(mask_r1, mask_r2)
    # Restrict stitches to ball area and thin lines
    mask_red = cv2.bitwise_and(mask_red, mask_red, mask=ball_mask)
    # Thin the mask to reduce fill leakage
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel2)

    # Fill mask (ball interior excluding stitches)
    fill_mask = cv2.bitwise_and(ball_mask, cv2.bitwise_not(mask_red))

    # Bounding box around the ball
    x0 = max(x - radius, 0)
    y0 = max(y - radius, 0)
    x1 = min(x + radius, w)
    y1 = min(y + radius, h)

    # Extract regions
    ball_region = bgr[y0:y1, x0:x1].copy()
    fill_region_mask = fill_mask[y0:y1, x0:x1]

    # Prepare RGBA if needed
    if alpha is not None:
        alpha_region = alpha[y0:y1, x0:x1]
    else:
        alpha_region = None

    # Rotate fill region by 90 degrees using affine warp (keeps same crop size)
    angle = -90 if clockwise else 90
    w_crop = x1 - x0
    h_crop = y1 - y0
    center = (w_crop / 2.0, h_crop / 2.0)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(ball_region, M, (w_crop, h_crop), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    rotated_mask = cv2.warpAffine(fill_region_mask, M, (w_crop, h_crop), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT)
    if alpha_region is not None:
        rotated_alpha = cv2.warpAffine(alpha_region, M, (w_crop, h_crop), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    else:
        rotated_alpha = None

    # Build new region by replacing only fill pixels
    rotated_region = ball_region.copy()
    mask_bool = rotated_mask.astype(bool)
    rotated_region[mask_bool] = rotated[mask_bool]

    # Place rotated_region back into image
    out = bgr.copy()
    out[y0:y1, x0:x1][mask_bool] = rotated_region[mask_bool]

    # Reattach alpha if present
    if alpha is not None:
        out_rgba = np.dstack((out, alpha))
        cv2.imwrite(output_path, out_rgba)
    else:
        cv2.imwrite(output_path, out)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/rotate_ball.py <input.png> [output.png]")
        sys.exit(1)
    inp = sys.argv[1]
    outp = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(inp)[0] + ' - ball-rotated.png'
    rotate_fill_only(inp, outp, clockwise=True)
    print(f"Wrote: {outp}")
