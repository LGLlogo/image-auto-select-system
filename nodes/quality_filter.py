import cv2
from core.node import Node


# 清晰度过滤
class QualityFilterNode(Node):
    name = 'quality_filter'

    def run(self, ctx):
        def calculate_sharpness(image):
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return cv2.Laplacian(gray, cv2.CV_64F).var()

        def check_exposure(image):
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            mean = gray.mean()
            return mean

        scored = []
        images = ctx.get("images")
        for path in images:
            img = cv2.imread(path)
            h, w = img.shape[:2]
            sharpness = calculate_sharpness(img)
            exposure = check_exposure(img)

            score = 0
            if sharpness > 100:
                score += 1
            if 80 < exposure < 180:
                score += 1
            if w > 3000 or h > 3000:
                score += 1

            scored.append((path, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        ctx.set("images", [i[0] for i in scored[:50]])

        print("After quality filter:", len(ctx.get("images")))
