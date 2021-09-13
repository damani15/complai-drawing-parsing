import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib.pyplot as plt
import os
import glob

class DXFImageTiler:
    """
    A class that turns a DXF file into a set of zoomed image tiles.
    """

    def __init__(self, dxf):
        """
        Arguments:
        dxf - Either an ezdxf document (loaded from a DXF file) or
        the path to a DXF file
        """

        if type(dxf) == str:
            self.doc = ezdxf.readfile(dxf)
        else:
            self.doc = dxf

        self.dpi = 300


    def make_figure(self):
        """
        Create a plot of the current document.
        Returns: The figure and its associated axes
        """

        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ctx = RenderContext(self.doc)
        out = MatplotlibBackend(ax)
        Frontend(ctx, out).draw_layout(self.doc.modelspace(), finalize=True)
        return fig, ax


    def make_tiles(self, x_size, y_size, x_step, y_step, output_path, verbose=True):
        """
        Created a set of zoomed tiles of the current document. That is done by
        sliding a window over the surface of the complete plot and extracting
        subplots. The size of the window and the size of the step to take while
        sliding are specified as arguments.

        Arguments:

          x_size: The width of the window along the x dimension
          y_size: The height of the window along the y dimension
          x_step: The distance to step the window along the x dimension
          y_step: The distance to step the window along the y dimension

        Returns: A list of tuples of the form (figure, xlim, ylim) where
        figure is the figure
        """

        fig, ax = self.make_figure()
        x = self.doc.header['$EXTMIN'][0]
        y = self.doc.header['$EXTMIN'][1]

        # Slide until the bottom edge of the window is above the top of
        # the elements in the doc
        while y < self.doc.header['$EXTMAX'][1]:

            # Get window into document
            xlim = (x, x + x_size)
            ylim = (y, y + y_size)
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)

            # to check if image is empty
            # import cv2
            # im = cv2.imread('2.jpg')
            # if im is None:
            #     Print("Image is empty")

            # to get percentage of empty space in image
            # from PIL import Image
            # image = Image.open("pepper.png")
            # bg = image.getpixel((0,0))
            # width, height = image.size
            # bg_count = next(n for n,c in image.getcolors(width*height) if c==bg)
            # img_count = width*height - bg_count
            # img_percent = img_count*100.0/width/height

            filename = "%s_x_%s_%s_y_%s_%s.png" % ("tile_", xlim[0], xlim[1], ylim[0], ylim[1])
            if verbose:
                print('Writing: %s' % filename)
            fig.savefig(os.path.join(output_path, filename), dpi=self.dpi)

            # Step
            x += x_step
            if x > self.doc.header['$EXTMAX'][0]:
                x = self.doc.header['$EXTMIN'][0]
                y += y_step


dxf_files = glob.glob('/home/sage08ai/Desktop/detectron_full/1.sample dxfs/*.dxf')
for dxf in dxf_files:
    print("processing file ", dxf)
    output_path = dxf.replace("1.sample dxfs", "4.tiles_black")
    output_path = output_path.rstrip('.dxf')
    os.makedirs(output_path, exist_ok=True)
    print(output_path)
    tiler = DXFImageTiler(dxf)
    tiler.make_tiles(300, 300, 250, 250, output_path = output_path, verbose=True)
    print("=="*30)
