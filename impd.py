import streamlit as st
from PIL import Image
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import tempfile
import os

def convert_images_to_pdf(images):
    temp_image_files = []  # Keep track of temporary files
    pdf_path = None
    
    try:
        # Create a temporary file to store the PDF
        pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf_path = pdf_file.name
        pdf_file.close()

        # Create the PDF with reportlab
        c = canvas.Canvas(pdf_path, pagesize=letter)
        
        for img in images:
            # Create a temporary file for each image
            img_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_image_files.append(img_temp.name)  # Store the filename for cleanup
            
            # Write the image data to the temporary file
            img_temp.write(img.getvalue())
            img_temp.close()  # Close the file immediately
            
            # Open the image using PIL
            with Image.open(temp_image_files[-1]) as pil_img:
                # Get the dimensions of the image
                img_width, img_height = pil_img.size
                
                # Calculate aspect ratio
                aspect = img_height / float(img_width)
                
                # Set maximum width and calculate height based on aspect ratio
                max_width = 500
                width = max_width
                height = width * aspect
                
                # Draw the image on the PDF
                c.drawImage(temp_image_files[-1], 50, letter[1] - height - 50, 
                          width=width, height=height)
                
                # Add a new page for the next image
                c.showPage()
        
        # Save the PDF
        c.save()
        return pdf_path
        
    except Exception as e:
        # If there's an error, make sure to clean up any created files
        if pdf_path and os.path.exists(pdf_path):
            try:
                os.unlink(pdf_path)
            except:
                pass
        raise e
        
    finally:
        # Clean up all temporary image files
        for temp_file in temp_image_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass

def main():
    st.title("Image to PDF Converter")
    st.write("Upload multiple images to convert them into a single PDF file.")
    
    # File uploader allows multiple files
    uploaded_files = st.file_uploader("Choose images", accept_multiple_files=True, 
                                    type=['png', 'jpg', 'jpeg'])
    
    if uploaded_files:
        st.write(f"Number of images uploaded: {len(uploaded_files)}")
        
        # Show uploaded images
        cols = st.columns(3)
        for idx, uploaded_file in enumerate(uploaded_files):
            with cols[idx % 3]:
                st.image(uploaded_file, caption=f"Image {idx + 1}", 
                        use_container_width=True)
        
        # Convert button
        if st.button("Convert to PDF"):
            if len(uploaded_files) > 0:
                with st.spinner("Converting images to PDF..."):
                    try:
                        # Convert images to PDF
                        pdf_path = convert_images_to_pdf(uploaded_files)
                        
                        # Read the generated PDF for download
                        with open(pdf_path, "rb") as file:
                            pdf_data = file.read()
                        
                        # Create download button
                        st.download_button(
                            label="Download PDF",
                            data=pdf_data,
                            file_name="converted_images.pdf",
                            mime="application/pdf"
                        )
                        
                        # Clean up the PDF file
                        try:
                            os.unlink(pdf_path)
                        except:
                            pass
                        
                        st.success("Conversion completed! Click the download button above to get your PDF.")
                    except Exception as e:
                        st.error(f"An error occurred during conversion: {str(e)}")
            else:
                st.error("Please upload at least one image.")

if __name__ == "__main__":
    main()