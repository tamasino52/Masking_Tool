# Masking_Tool
Segmentation masking tool using watershed transform. Draw your object easily!


# Requirement
You should move to 'Masking_Tool' folder, then input this command on console.
```
pip install -r requirement.txt
```
# Open file
After download all library, open python file according to language.
```
// English
python main.py

// Korean
python main.py --korean
```
# How to use
1. Select your Image folder path
<p align="center">
  <img src="/test/1.JPG">
</p>

2. Select folder path where you wanna save mask
<p align="center">
  <img src="/test/2.JPG">
</p>

3. In Brush Setting, you can change brush thickness and colors. You can control thickness by mouse wheel Too, also control colors by keyboard 1,2,3,4,5,6,7,8,9,0,-,=
<p align="center">
  <img src="/test/3.JPG">
</p>

4. You can move to other images to press this button and dial. Check combobox if you want it to be saved automatically every time you move to the next image. Also you can control all of these things in keyboard. (KEY LEFT, KEY RIGHT, KEY SPACE) Be careful not to save automatically when using dials.
<p align="center">
  <img src="/test/4.JPG">
</p>

5. Press Save Image button to save mask on Mask Folder you choose. If you mess up the picture, press the Repatin Image button to redraw it. Also you can control all of these things in keyboard. (KEY S, KEY R)
<p align="center">
  <img src="/test/5.JPG">
</p>

6. Paint and Enjoy!
<p align="center">
  <img src="/test/6.JPG">
</p>

# Caution
In your Image folder, It does not work if there are files other than images. This program does not guarantee that JPG, PNG, GIF, JPEG files or other image formats are supported. Mask files are always stored in the same format as image files. We developed in Python 3.6 and did not test running in other versions. If you leave a comment because of a problem while using it, I will correct it. Thanks.

# Update
It used to be 12 colors, but now it's 21 colors. Previously, the stored mask type was the same as the existing image type. However, we found a bug with mixed colors in the edges and modified it to be stored only in a bitmap file.
