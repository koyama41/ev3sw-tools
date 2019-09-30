# ev3sw-tools
Tools manipulating ".ev3p" files (programs of LEGO Mindstorms EV3 Software)

"LEGO Mindstroms EV3 Software" (which can be downloaded from https://education.lego.com )
handles "*.ev3" files, which contains an user program for a Mindstroms-EV3 robot.

A "*.ev3" file is a ZIP-compressed file:
You can easily manipulate inside of a "*.ev3" file by renaming it to "*.zip".
If You extract the zip file, you can find some "*.ev3p" files,
which corresponds to a My-Block (or the main program itself) of EV3 software.
A "*.ev3p" files is a XML file which is representing the structure of the diagram of the My-Block.

This repository contains a tool (or more tools in the future) to convert the XML of a "*.ev3p" file
into some human-readable texts.
With this tool, you can easily do some text-based manipulation such as:
  * get the difference between two "*.ev3p" files (use "diff" command)
  * find where a variable or My-Block is used in the entire "*.ev3" project by its name (use "grep" command)
  * and so on...
