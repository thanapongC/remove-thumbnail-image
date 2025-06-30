import os
from PIL import Image, ImageFilter, UnidentifiedImageError
import imagehash

# ฟังก์ชันในการคำนวณความคมชัดของภาพ
def calculate_sharpness(image_path):
    image = Image.open(image_path)
    image = image.convert("L")  # แปลงเป็นภาพขาวดำเพื่อคำนวณความคมชัด
    image = image.filter(ImageFilter.FIND_EDGES)
    return image.filter(ImageFilter.MedianFilter(5)).getextrema()[1]

# ฟังก์ชันในการหาคุณภาพของภาพจากขนาดไฟล์
def get_image_quality(image_path):
    return os.path.getsize(image_path)

# ฟังก์ชัน resize ภาพให้ขนาดเท่ากัน
def resize_image(image, size=(512, 512)):
    return image.resize(size, Image.Resampling.LANCZOS)

# เปรียบเทียบภาพโดยใช้แฮช
def compare_images(image1_path, image2_path):
    print(f"Comparing {image1_path} and {image2_path}...")
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)
    
    # Resize ภาพทั้งสองให้มีขนาดเท่ากันก่อน
    image1_resized = resize_image(image1)
    image2_resized = resize_image(image2)
    
    # เปรียบเทียบ hash ของภาพที่ถูก resize แล้ว
    hash1 = imagehash.phash(image1_resized)
    hash2 = imagehash.phash(image2_resized)
    
    return hash1 - hash2

# ลบภาพที่คุณภาพต่ำกว่า
def remove_duplicate_images(image_paths):
    unique_images = {}
    
    for image_path in image_paths:
        try:
            print(f"Processing image: {image_path}")
            # ตรวจสอบว่าไฟล์เป็นไฟล์ภาพ
            image = Image.open(image_path)
            image_hash = imagehash.phash(resize_image(image))  # Resize ก่อน hash
        except UnidentifiedImageError:
            # ถ้าไม่ใช่ไฟล์ภาพ ให้ข้ามไป
            print(f"Skipping non-image file: {image_path}")
            continue
        
        if image_hash in unique_images:
            current_best = unique_images[image_hash]
            current_quality = calculate_sharpness(current_best)
            new_quality = calculate_sharpness(image_path)
            
            # แสดงผลเมื่อทำการเปรียบเทียบคุณภาพ
            print(f"Comparing quality of {image_path} and {current_best}...")

            # ถ้าภาพใหม่มีคุณภาพดีกว่า ให้แทนที่ภาพเก่า
            if new_quality > current_quality:
                print(f"Removing lower quality image: {current_best}")
                os.remove(current_best)  # ลบภาพที่คุณภาพต่ำกว่า
                unique_images[image_hash] = image_path
            else:
                print(f"Removing lower quality image: {image_path}")
                os.remove(image_path)  # ลบภาพใหม่ที่คุณภาพต่ำกว่า
        else:
            unique_images[image_hash] = image_path

# ฟังก์ชันหลักในการค้นหาโฟลเดอร์ปีและเดือนใน wp-content/uploads
def process_wordpress_uploads(base_upload_folder):
    for year_folder in os.listdir(base_upload_folder):
        year_path = os.path.join(base_upload_folder, year_folder)
        
        if os.path.isdir(year_path):
            print(f"Processing year folder: {year_folder}")
            for month_folder in os.listdir(year_path):
                month_path = os.path.join(year_path, month_folder)
                
                if os.path.isdir(month_path):
                    print(f"Processing month folder: {month_folder}")
                    image_paths = [os.path.join(month_path, f) for f in os.listdir(month_path) if f.endswith(('.jpg', '.jpeg', '.png'))]
                    remove_duplicate_images(image_paths)

# ตัวอย่างการใช้งาน
wordpress_upload_folder = "/Users/nattapornsangsoda_1/Desktop/atpskin/wp-content/uploads"
process_wordpress_uploads(wordpress_upload_folder)
