
# PiArtAI - Raspberry Pi Zero Generative Art E-Paper Frame

PaperPiAI is a standalone Raspberry Pi Zero 2 powered e-ink picture frame
running stable diffusion generating an infinite array of pictures.

This default set-up generates random flower pictures with random styles that
I've found to work particularly well on a 7-colour
e-ink display, i.e. low-colour palette styles and simple designs.

Once set up the picture frame is fully self-sufficient, able to generate unique
images with no internet access until the end of time (or a hardware failure -
which ever comes first).

Each image takes about 1h10 minutes to generate and about 30 seconds to refresh
to the screen.  You can change the list of image subjects and styles in the
prompt file or provide your own. Ideally I'd like to generate the image
prompts with a local LLM but have not found one that runs on the RPi Zero 2
yet. It would not have to run fast - just fast enough to generate a new prompt
within 23 hours to have a new picure every day.

OnnxStream now supports custom resolutions for Stable Diffusion XL Turbo 1.0
so we can render directly for the display size. If for some reason you cannot
make use of this feature (e.g. using a different model) there is support
to use 'intelligent' cropping that uses [salient spectral feature
analysis](https://towardsdatascience.com/opencv-static-saliency-detection-in-a-nutshell-404d4c58fee4)
to guide the crop (landscape or portrait) towards most interesting part of
the image. This was needed in an earlier version when we could only generate
512x512 images.

# Acknowledgments

Based on PaperPiAI : [dylski's PpaerPiAI](https://github.com/dylski/PaperPiAI). This project has been largely based on PaperPiAI with a few tweaks for my needs. All credit goes to them for making this awesome project.


# Install

* **Raspberry Pi Zero 2**
* **Inky Impression 7.3"** 7-colour e-ink display. For Waveshare displays, see
  [here](https://github.com/dylski/PaperPiAI/issues/12#issuecomment-2603268581)
* OR Waveshare 5.65 inch 7 color display 
* Picture frame, ideally with deep frame to accommodate RPi Zero
* Heatsink (optional) - I saw a max of 70°C (ambient was ~21°C) but one might
  be useful in a hot area or confined space
* **Raspbian Bullseye Lite**. I have failed to get it working on Trixie due to the system taking too much memory ([see here](https://github.com/dylski/PaperPiAI/issues/22#issuecomment-3718491877) for some guidelines) and Bookworm (which had odd slowdowns).

##  Increase swapfile size for compilation

Edit **/etc/dphys-swapfile** (e.g. `sudo vim /etc/dphys-swapfile`) and change
the value of **CONF_SWAPSIZE** to 1024. You _might_ be able to get away with a
smaller swap size but it's been reported that the build process stalls with a
swap size of 256.

Then restart swap with `sudo /etc/init.d/dphys-swapfile restart`

## Enable E-paper interfaces

run `sudo raspi-config` and enable **SPI interface** and **I2C interface**

## Install required components

Firstly download this repository somewhere with:

```
sudo apt install git
git clone https://github.com/obenchekroun/PiArtAI.git
```
Then run the installation script:
```
cd PiArtAI
scripts/install.sh
```
`scripts/install.sh` has all the commands needed to install all the required
system packages, python libraries and [OnnxStream](https://github.com/vitoplantamura/OnnxStream)
 - Stable Diffusion for the Raspberry Pi Zero.  If you are feeling brave then
run `install.sh` in the directory you want to install everything, otherwise run
each command manually.

The whole process takes a _long_ time, i.e. several hours. If you are building
in a RPi 4 or 5 you can speed it up by appending ` -- -j4`  or ` -- -all` to
the `cmake --build . --config Release` lines in `install.sh`. This instructs
the compiler to use four cores or all cores, respectively. This speed up does
not work on the RPi Zero 2 as it only has 512MB RAM. Also note that 8GB of
model parameters will be downloaded. Depending on your wifi signal and braodband
speed this can also take a long time. It is recommended to position the RPi such
that the e-ink display does not impair the wifi signal!

Apologies for the rather manual approach - my install-fu is not up to scratch!

## Installing omni-epd
PiArtAI relies on omni-epd to get compatibility with a arge number of screens.
In order to install it (this part is also handled with the script `install.sh`) :

``` Bash
cd PiArtAI/
source .venv/bin/activate
pip3 install --upgrade pip setuptools wheel
pip3 install git+https://github.com/robweber/omni-epd.git#egg=omni-epd
```



In `display_picture.py`, configure the correct display using the variables :

``` python
DISPLAY_TYPE = "waveshare_epd.epd5in65f" #
DISPLAY_RESOLUTION = (600, 448)
```

Note that omni-epd uses `omni-epd.ini` as a config file, see its contents for options.

# Generating and displaying

## Generating

You need to run `generate_picture.py` with the resolution of the display and a
target directory to save the images. The Inky Impressions has a resolution of
800x480 so for a landscape image the command would be:

``` Bash
python3 generate_picture.py --width=800 --height=480 output_dir # for Pimoroni 7.3 inch screen
python3 generate_picture.py --width=600 --height=448 output_dir # for waveshare 5.65inch screen
```

This generates a new image with a unique name based on the prompt, and a copy
called 'output.png' to make it simple to display.

Note that if you install the python packages into a virtual env (as the script
above does) then you need to use that python instance, e.g.:

`.venv/bin/python3 src/generate_picture.py --width=800
--height=480 /tmp`

For more options, run the `generate_picture.py` script with the `-h` or `--help`
flags to see full usage.

## Displaying

To send to the display use `.venv/bin/python3 display_picture.py -r <image_name>`

Tie `-r` option skips any intelligent cropping (as this is no longer needed)
and just resizes the image to make sure it fits the display.

## Portrait display

To generate portrait images to display on portrait-oriented display switch the
width and height values for `generate_picture.py` and include the `-p` with the
display_picture.py script.  I.e. for the Inky Impression:

`.venv/bin/python3 generate_picture.py --width=480 --height=800 output_dir`

and 

`.venv/bin/python3 display_picture.py -r -p output_dir/output.png`


For more options, run the `display_picture.py` script with the `-h` or `--help`
flags to see full usage.

## Automating

To automate and generate an image per day for example, you can customise the executable script called `run_flower.sh` that runs the generation and display the image. 

```#!/bin/bash
#! /usr/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd ${SCRIPT_DIR}
source .venv/bin/activate
python3 generate_picture.py --width 600 --height 448 images/
python3 display_picture.py -r images/output.png
```
Obviously change yours to point to where your code is, and adapt `--width --height` argument to display size.
Make it executable :

``` Bash
chmod +x run_flower.sh
```

Then add the entry in crontab (run `crontab -e` to edit your crontab file):
`0 0 * * * /home/pi/PiArtAI/cron_flower.sh`
to run `cron_flower` every day at midnight.

Note that e-paper displays are suspectible to temperature. Depending on your Pi Zero's environment, it  may get hot for an extended period of time which could cause the display to render with some discoloration. This can be avoided by delaying the display update after generating the image.

## Prompts
The `prompts` directory stores JSON files which can be used to provide promps.
A prompt file is simply just an array of array of prompt fragments, one option
is chosen from each array at random and it is concatenated together. Custom
prompts can be provided with the `--prompt` option, or the file to use can be
specified with the `--prompts` option.

# Storage

All the generated images are currently retained locally. Each image is ~1.2MB
(assuming 800x480px resolution), so generating an image every 24 hours for
2.25 years would take up ~1GB storage. If you are generating images at a faster
rate and/or storage is limited then this would lead to issues.

A simple fix is to not save images with unique names, i.e. change [this line](
https://github.com/dylski/PaperPiAI/blob/main/src/generate_picture.py#L38) from

`fullpath = os.path.join(output_dir, f"{unique_arg}.png")`

to

`fullpath = os.path.join(output_dir, shared_file)`

and comment out lines 61 - 63.

Here is a complete Markdown section for your `PaperPiAI` README.

-----

## Button Control for Image Cycling and Shutdown (`display_buttons.py`)

The `display_buttons.py` script monitors the physical buttons attached to your Inky display.
It allows you to cycle through your processed images, select specific ones, and execute a shutdown command without needing to access a desktop or SSH session.

### Button Functionality

| Button | GPIO Pin (BCM) | Functionality |
| :----: | :------------: | :------------ |
| **A** | 5              | Selects and displays the **Latest** generated image (newest timestamp). |
| **B** | 6              | **Step Backwards** in time (selects the next **Oldest** image relative to the current `output.png`). |
| **C** | 25 / 16\* | **Step Forwards** in time (selects the next **Newest** image relative to the current `output.png`). |
| **D** | 24             | Executes **`sudo shutdown now`** to safely power down the Raspberry Pi. |

\* **Note on Button C Pin:** The script defines the pin for Button C as **25** for users with the **Inky Impression 13.3"** display. If you are using an Inky Impression 7.3" or other common pHATs, change the `SW_C` value in the script from `25` back to **`16`** to ensure proper operation.

-----

## Install GPIO modules

```bash
.venv/bin/python -m pip install gpiod
.venv/bin/python -m pip install gpiodevice
```

## Running on Boot (Systemd Service)

To ensure the button monitoring starts automatically and runs reliably in the background, you should set it up as a **Systemd Service**.

### 1\. Create the Service File

Create a new service definition file using `sudo`:

```bash
sudo nano /etc/systemd/system/display-button-monitor.service
```

Paste the following content, ensuring the `User` and `ExecStart` path match your environment:

```ini
[Unit]
Description=PiArtAI Button Monitor (gpiod)
# Wait for basic networking, but not for the desktop environment
After=network.target

[Service]
# Replace 'pi' with your actual username
User=pi
# Adjust the path to where your virtual environment and script are located
ExecStart=/home/pi/PiArtAI/.venv/bin/python3 /home/pi/PaperPiAI/display_buttons.py
# If the script exits unexpectedly, restart it after 5 seconds
Restart=always
RestartSec=5

[Install]
# Ensure it is started during the multi-user boot phase
WantedBy=multi-user.target
```

### 2\. Enable and Start the Service

Use the following commands to register, enable, and start the monitor:

```bash
# Reload the systemd manager configuration
sudo systemctl daemon-reload

# Enable the service to start automatically on every boot
sudo systemctl enable display-button-monitor.service

# Start the service immediately
sudo systemctl start display-button-monitor.service

# Check the service status and logs
sudo systemctl status display-button-monitor.service
```

The script will now run silently in the background, waiting for button presses.
