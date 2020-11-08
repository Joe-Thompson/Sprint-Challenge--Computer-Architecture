import sys

# Program Actions
LDI = 0b10000010  # LOAD IMMEDIATE
PRN = 0b01000111  # PRINT
HLT = 0b00000001  # HALT
ADD = 0b10100000  # ADD
MUL = 0b10100010  # MULTIPLY
PUSH = 0b01000101  # PUSH onto stack
POP = 0b01000110  # POP off stack
CALL = 0b01010000  # CALL subroutine
RET = 0b00010001  # RETURN


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256  # 256 bytes of memory
        self.registers = [0] * 8  # General Purpose Registers 0 - 7
        self.pc = 0  # Program Counter
        self.sp = 7  # Stack Pointer
        self.running = False

        self.branch_table = {LDI: self.ldi, PRN: self.prn, HLT: self.hlt, ADD: self.add, MUL: self.mul, PUSH: self.push,
                             POP: self.pop, CALL: self.call, RET: self.ret}

    # access the RAM inside the CPU object
    # MAR (Memory Address Register) - contains the address that is
    # being read / written to
    def ram_read(self, MAR):
        # accepts the address to read and return the value stored there
        return self.ram[MAR]

    # access the RAM inside the CPU object
    # MDR (Memory Data Register) - contains the data that was read or
    # the data to write
    def ram_write(self, MAR, MDR):
        # accepts a vale to write and the address to write it to
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print("Usage: ls8.py filename")
            sys.exit(1)

        try:
            address = 0
            with open(sys.argv[1]) as f:
                for line in f:
                    split_line = line.split('#')
                    program_instruction = split_line[0].strip()

                    if program_instruction == '':
                        continue

                    try:
                        program_instruction = int(program_instruction, 2)

                    except ValueError:
                        print(f"Invalid instruction: {program_instruction}")
                        sys.exit(1)

                    self.ram_write(address, program_instruction)
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[1]} file not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]

        elif op == "MUL":
            self.registers[reg_a] *= self.registers[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    # Function for add and multiply operations
    def op_helper(self, op):
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.alu(op, operand_a, operand_b)
        self.pc += 3

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.registers[i], end='')

        print()

    # Branch Table Commands
    def ldi(self):
        # gets the address for registry
        operand_a = self.ram[self.pc + 1]
        # gets the value for the registry
        operand_b = self.ram[self.pc + 2]
        # Assign value to Reg Key
        self.registers[operand_a] = operand_b
        # Update PC
        self.pc += 3

    def prn(self):
        # get the address we want to print
        operand_a = self.ram[self.pc + 1]
        # Print Reg
        print(self.registers[operand_a])
        # Update PC
        self.pc += 2

    def hlt(self):
        # Exit Loop
        self.running = False
        # Update PC
        self.pc += 1

    def add(self):
        self.op_helper("ADD")

    def mul(self):
        self.op_helper("MUL")

    def push(self):
        given_register = self.ram[self.pc + 1]
        value_in_register = self.registers[given_register]
        # Decrement the stack pointer
        self.registers[self.sp] -= 1
        # Write the value of the given register to memory at SP location
        self.ram[self.registers[self.sp]] = value_in_register
        self.pc += 2

    def pop(self):
        given_register = self.ram[self.pc + 1]
        # write the value in memory at the top of stack to the given register
        value_from_memory = self.ram[self.registers[self.sp]]
        self.registers[given_register] = value_from_memory
        # increment the stack pointer
        self.registers[self.sp] += 1
        self.pc += 2

    def call(self):
        # Get the given register in the operand
        given_register = self.ram[self.pc + 1]
        # Store the return address (PC + 2) onto the stack
        # decrement the stack pointer
        self.registers[self.sp] -= 1
        # write the return address
        self.ram[self.registers[self.sp]] = self.pc + 2
        # set pc to the value inside the given_register
        self.pc = self.registers[given_register]

    def ret(self):
        # set the pc to the value at the top of the stack
        self.pc = self.ram[self.registers[self.sp]]
        # pop from stack
        self.registers[self.sp] += 1

    def run(self):
        """Run the CPU."""

        self.running = True
        # self.registers[self.sp] = len(self.ram)

        while self.running:
            # read the memory address (MAR) that's stored in register PC (self.pc)
            # store the result in instruction_register
            instruction_register = self.pc
            instance = self.ram[instruction_register]

            try:
                self.branch_table[instance]()

            except KeyError:
                print(f"KeyError at {self.registers[self.ram[instance]]}")
                sys.exit(1)
