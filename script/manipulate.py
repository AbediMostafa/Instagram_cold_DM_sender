
import cv2
from skimage.metrics import structural_similarity as ssim
import numpy as np

# Load the two images
image1 = cv2.imread('1.jpg', cv2.IMREAD_GRAYSCALE)
image2 = cv2.imread('3.jpg', cv2.IMREAD_GRAYSCALE)

# Resize the second image to match the dimensions of the first image
image2_resized = cv2.resize(image2, (image1.shape[1], image1.shape[0]))

# Compute SSIM between the two images
similarity_index, diff = ssim(image1, image2_resized, full=True)
print(f"SSIM Similarity Index: {similarity_index}")

# Feature matching using ORB
orb = cv2.ORB_create()
keypoints1, descriptors1 = orb.detectAndCompute(image1, None)
keypoints2, descriptors2 = orb.detectAndCompute(image2_resized, None)

# Match features
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(descriptors1, descriptors2)
matches = sorted(matches, key=lambda x: x.distance)

# Draw matches
matched_image = cv2.drawMatches(image1, keypoints1, image2_resized, keypoints2, matches[:10], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
cv2.imshow('Matches', matched_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Print the number of matches
print(f"Number of matches: {len(matches)}")