# MIOS
NIOS compatible ISS in py4hw


### Building Bare-Metal SW

Open a NIOS2 command shell

```
nios2_command_shell.sh
```

Currently we provide two examples using 7-segment displays:

- Using a Bus-Attached device 
- Using a Custom-Instruction attached device


To compile, 

```
cd software/testLEDBus
make hex
```

The compilation will produce an hex file that will be loaded in the instruction memory in the testbench


### Running the System Testbench

Run the tb_MiosBus script

```
python tb_MiosBus.py
```


### Running a Buildroot distribution

Run the tb_MiosBuildroot script

```
python -i tb_MiosBuildroot.py
```

some functions can be called as an interactive command-line debugger (i.e. regs, step, tbreak, go, ...)
