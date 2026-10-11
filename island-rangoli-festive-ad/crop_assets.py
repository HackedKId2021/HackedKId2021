"""Cut brand imagery out of the islandrangoli.com screenshots (site itself isn't reachable)."""
import sys
from pathlib import Path
from PIL import Image, ImageFilter

src = Path(sys.argv[1])
out = Path(__file__).parent / "assets"
I = lambda n: Image.open(src / f"{n}.webp").convert("RGB")

crops = {
    # products (Mega Festive Sale / Best Sellers cards)
    "p_deepdwar":  (4, (411, 680, 672, 941)),
    "p_swarn":     (4, (703, 680, 984, 961)),
    "p_varn":      (4, (1016, 680, 1297, 961)),
    "p_mandapam":  (4, (1328, 680, 1589, 941)),
    "p_shikha":    (3, (703, 387, 984, 668)),
    "p_nity":      (3, (1016, 387, 1297, 668)),
    "p_leaves":    (3, (391, 1009, 672, 1290)),
    # lifestyle / instagram grid
    "l_lanterns":  (1, (0, 611, 481, 1091)),
    "l_sofa":      (1, (506, 611, 987, 1091)),
    "l_boxes":     (1, (1013, 611, 1494, 1091)),
    "l_navratri":  (1, (0, 133, 481, 585)),
    "l_kolam":     (1, (506, 133, 987, 585)),
    "l_diyas":     (1, (1519, 133, 2000, 585)),
    # categories
    "c_colors":    (4, (1103, 217, 1358, 472)),
    "c_rangoli":   (4, (303, 217, 558, 472)),
    "c_mayur":     (4, (703, 217, 958, 472)),
    # hero banner + emblem
    "hero":        (5, (36, 293, 1290, 1200)),
    "emblem":      (5, (1479, 357, 1626, 504)),
}
for name, (n, box) in crops.items():
    im = I(n).crop(box)
    im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    im.save(out / f"{name}.jpg", quality=93)
    print(name, im.size)
