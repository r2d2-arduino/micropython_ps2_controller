"""
PS2_Controller v 0.1.3
 
Project path: https://github.com/r2d2-arduino/micropython_ps2_controller
MIT License

Author: Arthur Derkach
"""
from time import sleep_us, sleep_ms
from machine import Pin

VALID_MODES = [0x41, 0x73]

CMD_CONFIG_ENTER = [0x01, 0x43, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00]

CMD_CONFIG_MODE = [0X01, 0x44, 0x00,
            0x01,  # joystick's mode: 00 = normal; 01 = analog
            0x00,  # analog lock: 03 = on; 00 = off
            0x00, 0x00, 0x00, 0x00]

CMD_CONFIG_EXIT = [0x01, 0x43, 0x00, 0x00, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A]

CMD_READ_DATA = [0x01, 0x42, 0x00,
                 0x00, # motor ctrl (if config is set): 0x00..0xFF
                 0x00, # motor ctrl (if config is set): 0x00..0xFF
                 0x00, 0x00, 0x00, 0x00]

CMD_MOTOR_ENABLE = [0x01, 0x4D, 0x00,
                    0x00, # small motor ctrl: 0x00 = on; 0x01 = off
                    0x01, # large motor power: 0x00..0x40 (hi -> low)
                    0xFF, 0xFF, 0xFF, 0xFF] 

CMD_SET_DATA_LARGE = [0x01, 0x4F, 0x00, 0xFF, 0xFF, 0x03, 0x00, 0x00, 0x00]

CMD_READ_DATA_LARGE = [0x01, 0x42, 0x00,
                 0x00, # motor ctrl (if config is set): 0x00..0xFF
                 0x00, # motor ctrl (if config is set): 0x00..0xFF
                 0x00, 0x00, 0x00, 0x00,
                 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

CMD_GET_STATUS = [0x01, 0x45, 0x00, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A]
    
class PS2_Controller:

    def __init__(self, data_pin=13, cmd_pin=12, cs_pin=15, clk_pin=14):
        ''' Main constructor
        Args:
        data_pin (int): Number of Data pin
        cmd_pin  (int): Number of Command pin
        cs_pin   (int): Number of CS/Attention pin
        clk_pin  (int): Number of Clock pin
        '''
        self.data = Pin(data_pin, Pin.IN) 
        self.cmd  = Pin(cmd_pin, Pin.OUT) 
        self.cs   = Pin(cs_pin,  Pin.OUT) # or Attention
        self.clk  = Pin(clk_pin, Pin.OUT)
        
        self.configure()
        
        result = self.send_commands( CMD_READ_DATA )
        sleep_ms(10)
        
        if result and result[1] in VALID_MODES:
            print("Controller configured correctly.")
            print("Press START to begin.")
        else:
            print("Something went wrong, unknown mode:", result[1])

    def configure(self):
        ''' Main controller configuration '''
        self.send_commands( CMD_CONFIG_ENTER )
        self.send_commands( CMD_CONFIG_MODE )
        #self.send_commands( CMD_MOTOR_ENABLE )
        self.send_commands( CMD_CONFIG_EXIT )
        sleep_ms(10)

    def send_command( self, command ):
        ''' Send command to controller
        Args:
        command (byte): Byte of command
        Return (byte): Byte of response
        '''
        response = 0
        clk, cmd, data = self.clk, self.cmd, self.data
        
        cmd.value(0)
        
        for i in range(8):
            cmd.value( ( command >> i ) & 1 )            
            clk.value(0)
            response |= ( data.value() << i )    
            clk.value(1)
            
        return response 

    def send_commands( self, commands ):
        ''' Send many commands to controller
        Args:
        commands (tuple of bytes): Bytes of commands
        Return (tuple of bytes): Bytes of response
        '''        
        result = []
        self.cs.value(0)
        
        for command in commands:
            result.append( self.send_command( command ) )
            
        self.cs.value(1)
        return result

    def read_keys(self):
        ''' Read pressed keys '''
        keys = ( 'SELECT', 'L3', 'R3', 'START', 'UP', 'RIGHT', 'DOWN', 'LEFT',
            'L2', 'R2', 'L1', 'R1', 'TRIANGLE', 'O', 'X', 'SQUARE' )

        data = self.send_commands( CMD_READ_DATA )
        
        if len(data) < 9:
            return [False, 127, 127, 127, 127]
        
        analog_mode = ( data[1] == 0x73 )
        pressed_keys = [ analog_mode, 127, 127, 127, 127 ]

        all_keys = ( data[4] << 8 ) | data[3]
        for i in range( 16 ):
            if not all_keys & (1 << i):
                pressed_keys.append( keys[i] )

        if analog_mode:
            pressed_keys[1] = data[5] # rx
            pressed_keys[2] = data[6] # ry
            pressed_keys[3] = data[7] # lx
            pressed_keys[4] = data[8] # ly
         
        return pressed_keys
