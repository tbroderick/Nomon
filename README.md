Nomon
================
This repository contains the Windows Installer for Nomon.

Nomon, invented by [Tamara Broderick](http://people.csail.mit.edu/tbroderick/index.html), is a keyboard application that uses a single switch selection method, allowing users to select a letter or a word with a single click. These clicks are distinguished by their timing, which can be controlled depending on the users desired speed. Each letter and suggested word is paired with a set of small clocks, each one associated with each option of a letter or a word. Repeatedly, when the clock's moving hand is at noon, the user clicks the single click until the desired option is selected. Using this method, users can select words and letters to form sentences with just a single switch.

Nomon has also been used in different applications such as games. GNOMON (Gaming Nomon) is a software developed based on Nomon presenting "action-oriented single switch video games" that allows children with disabilities to also enjoy video games [link](https://dl.acm.org/citation.cfm?id=3085957). This was a successful application of Nomon, allowing users with disability to overcome some barriers.

Relevant papers about Nomon include:
- Broderick, T and MacKay, DJC. Fast and flexible selection with a single switch. *PLoS ONE* 4(10), e7481. [link](http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0007481)
- Broderick, T. Nomon: Efficient communication with a single switch. *Technical Report* (extension of Master's Thesis). Cavendish Laboratory, University of Cambridge. [ps](http://www.inference.org.uk/nomon/files/nomon_tech_report.ps) [pdf](http://www.inference.org.uk/nomon/files/nomon_tech_report.pdf)

This is a [video]()
 of the past version of Nomon as described in the papers above.

Licensing 
================

Nomon Keyboard is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Nomon Keyboard is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Nomon Keyboard.  If not, see <http://www.gnu.org/licenses/>.

Installing Nomon on Windows
================
1. Download the latest installer from our google drive (https://drive.google.com/open?id=1VvtzymjkKMjzNXFzJ6oT12m_MjbWAV8B)
2. Choose a directory for Nomon (example (default): "C:\Program Files\Nomon")
3. "Do you want to allow an unknown publisher to make changes to your device?" may appear. If it does, click "yes."

We have succesfully tested the installer on Windows 7 and Windows 10.

Running Nomon on Windows
============
You can also watch [this video](https://youtu.be/fv-WvW0JktE) for instructions on running and using Nomon.
1. Locate the Nomon desktop icon (it is a yellow "N")
2. Click on the icon

If you get an error "IOError: [Errno13] Permission denied" error, you will need to run Nomon as Administrator:
1. Right click on the icon
2. Select "Run as Administrator" from the list of options
3. "Do you want this app from an unknown publisher to make changes to your device?" may appear. If it does, click "yes."

**Note:** At the moment the "talk" capabilities of Nomon are not part of the release. This will be included in a future release.

Troubleshooting
====================
**IOError: [Errno13] Permission denied**

Check that you are not using an old version of Nomon (version 2 or earlier). If this is the case--and you wish to install an older version--make sure you have not installed Nomon in the Program Files directory. You can resolve this issue permanently by reinstalling Nomon in a different dirctory (such as C:\Nomon), or you can run Nomon as Administrator (see instructions on how to do this in "Running Nomon").

How to Use Nomon:
====================
[This same video](https://youtu.be/fv-WvW0JktE) also has instructions for using Nomon.



