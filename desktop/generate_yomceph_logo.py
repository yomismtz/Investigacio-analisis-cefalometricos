from pathlib import Path
from PIL import Image, ImageDraw

SIZE = 512
BG = (110, 74, 158, 255)
RING = (220, 204, 242, 255)
INNER = (247, 241, 251, 255)
PURPLE = (78, 52, 116, 255)
TEAL = (67, 185, 168, 255)
MINT = (221, 244, 234, 255)
GOLD_DARK = (143, 107, 30, 255)
GOLD = (214, 173, 85, 255)
WHITE = (255, 253, 252, 255)


def generate(path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    im = Image.new('RGBA', (SIZE, SIZE), BG)
    d = ImageDraw.Draw(im)

    # Circular identity used by the 0.12.x desktop application.
    d.ellipse((42, 42, 470, 470), fill=RING)
    d.ellipse((72, 72, 440, 440), fill=INNER)

    # Left tooth outline.
    left = [(145,177),(121,194),(123,231),(133,258),(143,279),(151,310),
            (158,343),(166,362),(178,346),(190,322),(200,344),(212,362),
            (224,341),(235,310),(244,281),(254,259),(254,224),(250,184)]
    d.line(left, fill=PURPLE, width=12, joint='curve')

    # Right tooth outline.
    right = [(254,184),(278,180),(300,183),(321,202),(342,180),(366,178),
             (390,194),(389,229),(379,256),(370,279),(363,310),(355,342),
             (344,359),(332,342),(321,320),(309,342),(299,359),(288,343),
             (279,310),(269,280),(260,258),(254,229)]
    d.line(right, fill=PURPLE, width=12, joint='curve')

    # Pale green central tooth area behind the ruler.
    d.polygon([(260,184),(283,181),(301,184),(321,200),(342,180),(360,180),
               (360,233),(349,263),(341,291),(332,314),(321,318),(310,298),
               (298,318),(286,310),(278,281),(268,253),(260,229)], fill=MINT)
    d.line([(260,184),(283,181),(301,184),(321,200),(342,180),(360,180)], fill=PURPLE, width=10, joint='curve')

    # Turquoise cephalometric reference/calibration line.
    d.line((145,178,365,178), fill=TEAL, width=10)
    d.line((146,150,146,190), fill=TEAL, width=10)
    d.line((365,150,365,191), fill=TEAL, width=10)
    for x in (175, 211, 247, 283, 319, 350):
        d.line((x,159,x,181), fill=TEAL, width=7)

    # Golden set-square/ruler, the distinctive YomCeph mark.
    tri = [(166,329),(350,205),(350,330)]
    d.line(tri + [tri[0]], fill=GOLD_DARK, width=14, joint='curve')
    d.line((177,322,339,214), fill=GOLD, width=8)
    d.line((176,323,339,323), fill=GOLD, width=12)
    d.line((339,214,339,323), fill=GOLD, width=10)
    inner_tri = [(209,309),(320,235),(320,309)]
    d.polygon(inner_tri, fill=WHITE)
    d.line(inner_tri + [inner_tri[0]], fill=GOLD_DARK, width=7, joint='curve')

    # Purple reference nodes.
    d.ellipse((165,321,185,341), fill=PURPLE)
    d.ellipse((334,321,354,341), fill=PURPLE)

    im.save(path, optimize=True)
    return path


if __name__ == '__main__':
    out = generate(Path(__file__).parent / 'assets' / 'yomceph_logo.png')
    print(out)
