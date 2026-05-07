import gradio as gr
import tempfile
from PIL import Image

from pipeline.remove_bg import remove_background
from pipeline.extract_contour import extract_largest_contour, draw_contour_preview
from pipeline.build_mesh import build_cookie_cutter_mesh


def _get_contour(image, detail_level, pillow, alpha_threshold, blur_radius, close_kernel):
    rgba = remove_background(image)
    contour = extract_largest_contour(
        rgba,
        epsilon_factor=detail_level,
        alpha_threshold=alpha_threshold,
        blur_radius=blur_radius,
        close_kernel=close_kernel,
    )
    if pillow > 0:
        contour = contour.buffer(pillow, join_style="round")
    return contour


def preview_contour(
    image: Image.Image,
    detail_level: float,
    pillow: float,
    alpha_threshold: float,
    blur_radius: float,
    close_kernel: float,
) -> Image.Image:
    if image is None:
        raise gr.Error("Please upload an image first.")
    contour = _get_contour(image, detail_level, pillow, alpha_threshold, blur_radius, close_kernel)
    return draw_contour_preview(image, contour)


def generate_stl(
    image: Image.Image,
    wall_thickness: float,
    height: float,
    output_size: float,
    detail_level: float,
    pillow: float,
    alpha_threshold: float,
    blur_radius: float,
    close_kernel: float,
) -> tuple:
    if image is None:
        raise gr.Error("Please upload an image first.")

    contour = _get_contour(image, detail_level, pillow, alpha_threshold, blur_radius, close_kernel)
    preview = draw_contour_preview(image, contour)

    mesh = build_cookie_cutter_mesh(
        contour,
        wall_thickness_mm=wall_thickness,
        height_mm=height,
        image_size=(image.width, image.height),
        output_size_mm=output_size,
    )

    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
        mesh.export(f.name)
        return preview, f.name


with gr.Blocks(title="Cookie Cutter Generator") as demo:
    gr.Markdown(
        "# Cookie Cutter Generator\n"
        "Upload a photo of any shape and download a ready-to-print cookie cutter STL.\n\n"
        "> **Tip:** Works best with a subject on a plain or simple background. "
        "If the background is busy, remove it first with a tool like remove.bg."
    )

    with gr.Row():
        with gr.Column(scale=1):
            image_input = gr.Image(type="pil", label="Upload Image")
            detail_level = gr.Slider(
                minimum=0.001, maximum=0.01, value=0.002, step=0.001,
                label="Contour Detail",
                info="Lower = more detail, higher = smoother. Adjust until the preview looks right."
            )
            pillow = gr.Slider(
                minimum=0, maximum=50, value=0, step=1,
                label="Pillow (px)",
                info="Expands and rounds the contour outward. Makes the cookie profile softer."
            )
            with gr.Accordion("Advanced", open=False):
                alpha_threshold = gr.Slider(
                    minimum=1, maximum=254, value=127, step=1,
                    label="Alpha Threshold",
                    info="How transparent a pixel must be to count as background. Lower = include more of the subject."
                )
                blur_radius = gr.Slider(
                    minimum=1, maximum=21, value=5, step=2,
                    label="Mask Blur",
                    info="Smooths the alpha mask before tracing. Increase if the outline is speckled or rough."
                )
                close_kernel = gr.Slider(
                    minimum=1, maximum=31, value=7, step=2,
                    label="Gap Fill",
                    info="Fills small holes and breaks in the mask. Increase if the outline has gaps."
                )
            preview_btn = gr.Button("Preview Contour", variant="secondary", size="lg")
            contour_preview = gr.Image(label="Contour Preview")
            gr.Markdown("---")
            wall_thickness = gr.Slider(
                minimum=1.0, maximum=5.0, value=2.0, step=0.5,
                label="Wall Thickness (mm)",
                info="How thick the cutter walls are. 2mm is a good default."
            )
            height = gr.Slider(
                minimum=10.0, maximum=40.0, value=20.0, step=2.0,
                label="Cutter Height (mm)",
                info="How tall the cutter is. 20mm cuts through most dough."
            )
            output_size = gr.Slider(
                minimum=40.0, maximum=150.0, value=80.0, step=10.0,
                label="Max Size (mm)",
                info="Longest dimension of the finished cutter."
            )
            run_btn = gr.Button("Generate STL", variant="primary", size="lg")

        with gr.Column(scale=1):
            stl_output = gr.File(label="Download STL")
            gr.Markdown(
                "### After downloading\n"
                "Open the STL in your slicer (PrusaSlicer, Cura, etc.), "
                "slice with 2–3 perimeters and 0% infill, and print in PLA or PETG."
            )

    preview_btn.click(
        fn=preview_contour,
        inputs=[image_input, detail_level, pillow, alpha_threshold, blur_radius, close_kernel],
        outputs=contour_preview,
    )

    run_btn.click(
        fn=generate_stl,
        inputs=[image_input, wall_thickness, height, output_size, detail_level, pillow, alpha_threshold, blur_radius, close_kernel],
        outputs=[contour_preview, stl_output],
    )


if __name__ == "__main__":
    demo.launch()
