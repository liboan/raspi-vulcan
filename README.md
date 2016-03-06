# raspi-vulcan


I started this project as a foray into computer vision and hardware programming. It uses a Raspberry Pi and camera to look for a black rectangular target, then sends a command to an Arduino to rotate the camera using a servo. Ultimately my goal is to acquire hardware to create a full-fledged Nerf Vulcan turret which can detect and fire on targets.

In the screen capture below, the top window shows the output from the camera. The program uses the Canny edge detection algorithm to find contours (green), then finds and marks the target (red dot) by searching for two concentric, roughly rectangular-shaped contours.  

The bottom window shows the instructions received by the Arduino from the Pi. I wrote a simple protocol to allow the Pi to signal that an instruction was being sent.

[Video!](https://gfycat.com/LimpApprehensiveBighornsheep)

![Raspberry Pi screen capture of program](http://i.imgur.com/t63pqnu.png)
