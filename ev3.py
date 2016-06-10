#!/usr/bin/env python3

"""
LEGO EV3 direct commands
"""

# pylint: disable=invalid-name, too-many-lines, C0326

import socket
import usb.core
import struct
import re
import threading
import time
import datetime
import numbers, collections

WIFI      = 'W'                      
BLUETOOTH = 'B'
USB       = 'U'

STD       = 0                         # reply if global_mem, wait for reply
ASYNC     = 1                         # reply if global_mem, never wait for reply
SYNC      = 2                         # always with reply, always wait for reply

_ID_VENDOR_LEGO = 0x0694              # Usb-Identification of the device
_ID_PRODUCT_EV3 = 0x0005

_EP_IN  = 0x81                        # Usb-Endpoints
_EP_OUT = 0x01

WIFI      = 'W'
BLUETOOTH = 'B'
USB       = 'U'

_DIRECT_COMMAND_REPLY     = b'\x00'
_DIRECT_COMMAND_NO_REPLY  = b'\x80'

_DIRECT_REPLY             = b'\x02'
_DIRECT_REPLY_ERROR       = b'\x04'

opError                   = b'\x00'   # VM
opNop                     = b'\x01'
opProgram_Stop            = b'\x02'
opProgram_Start           = b'\x03'
opObject_Stop             = b'\x04'
opObject_Start            = b'\x05'
opObject_Trig             = b'\x06'
opObject_Wait             = b'\x07'
opObject_Return           = b'\x08'
opObject_Call             = b'\x09'
opObject_End              = b'\x0A'
opSleep                   = b'\x0B'
opProgram_Info            = b'\x0C'
# PROGRAM_INFO SUBCODES
OBJ_STOP                  = 0x00
OBJ_START                 = b'\x04'
GET_STATUS                = b'\x16'
GET_SPEED                 = b'\x17'
GET_PRGRESULT             = b'\x18'
SET_INSTR                 = b'\x19'

opLabel                   = b'\x0D'
opProbe                   = b'\x0E'
opDo                      = b'\x0F'
opAdd8                    = b'\x10'   # MATH
opAdd16                   = b'\x11'
opAdd32                   = b'\x12'
opAddf                    = b'\x13'
opSub8                    = b'\x14'
opSub16                   = b'\x15'
opSub32                   = b'\x16'
opSubf                    = b'\x17'
opMul8                    = b'\x18'
opMul16                   = b'\x19'
opMul32                   = b'\x1A'
opMulf                    = b'\x1B'
opDiv8                    = b'\x1C'
opDiv16                   = b'\x1D'
opDiv32                   = b'\x1E'
opDivf                    = b'\x1F'
opOr8                     = b'\x20'   # LOGIC
opOr16                    = b'\x21'
opOr32                    = b'\x22'
opAnd8                    = b'\x24'
opAnd16                   = b'\x25'
opAnd32                   = b'\x26'
opXor8                    = b'\x28'
opXor16                   = b'\x29'
opXor32                   = b'\x2A'
opRl8                     = b'\x2C'
opRl16                    = b'\x2D'
opRl32                    = b'\x2E'
opInit_Bytes              = b'\x2F'   # MOVE
opMove8_8                 = b'\x30'
opMove8_16                = b'\x31'
opMove8_32                = b'\x32'
opMove8_F                 = b'\x33'
opMove16_8                = b'\x34'
opMove16_16               = b'\x35'
opMove16_32               = b'\x36'
opMove16_F                = b'\x37'
opMove32_8                = b'\x38'
opMove32_16               = b'\x39'
opMove32_32               = b'\x3A'
opMove32_F                = b'\x3B'
opMovef_8                 = b'\x3C'
opMovef_16                = b'\x3D'
opMovef_32                = b'\x3E'
opMovef_F                 = b'\x3F'
opJr                      = b'\x40'   # BRANCH
opJr_False                = b'\x41'
opJr_True                 = b'\x42'
opJr_Nan                  = b'\x43'
opCp_Lt8                  = b'\x44'   # COMPARE
opCp_Lt16                 = b'\x45'
opCp_Lt32                 = b'\x46'
opCp_Ltf                  = b'\x47'
opCp_Gt8                  = b'\x48'
opCp_Gt16                 = b'\x49'
opCp_Gt32                 = b'\x4A'
opCp_Gtf                  = b'\x4B'
opCp_Eq8                  = b'\x4C'
opCp_Eq16                 = b'\x4D'
opCp_Eq32                 = b'\x4E'
opCp_Eqf                  = b'\x4F'
opCp_Ne8                  = b'\x50'
opCp_Ne16                 = b'\x51'
opCp_Ne32                 = b'\x52'
opCp_Nef                  = b'\x53'
opCp_Lte8                 = b'\x54'
opCp_Lte16                = b'\x55'
opCp_Lte32                = b'\x56'
opCp_Ltef                 = b'\x57'
opCp_Gte8                 = b'\x58'
opCp_Gte16                = b'\x59'
opCp_Gte32                = b'\x5A'
opCp_Gtef                 = b'\x5B'
opSelect8                 = b'\x5C'   # SELECT
opSelect16                = b'\x5D'
opSelect32                = b'\x5E'
opSelectf                 = b'\x5F'
opSystem                  = b'\x60'   # VM
opPort_Cnv_Output         = b'\x61'
opPort_Cnv_Input          = b'\x62'
opNote_To_Freq            = b'\x63'
opJr_Lt8                  = b'\x64'   # BRANCH
opJr_Lt16                 = b'\x65'
opJr_Lt32                 = b'\x66'
opJr_Ltf                  = b'\x67'
opJr_Gt8                  = b'\x68'
opJr_Gt16                 = b'\x69'
opJr_Gt32                 = b'\x6A'
opJr_Gtf                  = b'\x6B'
opJr_Eq8                  = b'\x6C'
opJr_Eq16                 = b'\x6D'
opJr_Eq32                 = b'\x6E'
opJr_Eqf                  = b'\x6F'
opJr_Neq8                 = b'\x70'
opJr_Neq16                = b'\x71'
opJr_Neq32                = b'\x72'
opJr_Neqf                 = b'\x73'
opJr_Lteq8                = b'\x74'
opJr_Lteq16               = b'\x75'
opJr_Lteq32               = b'\x76'
opJr_Lteqf                = b'\x77'
opJr_Gteq8                = b'\x78'
opJr_Gteq16               = b'\x79'
opJr_Gteq32               = b'\x7A'
opJr_Gteqf                = b'\x7B'
opInfo                    = b'\x7C'   # VM
    # INFO_SUBCODE
SET_ERROR                 = b'\x01'
GET_ERROR                 = b'\x02'
ERRORTEXT                 = b'\x03'
GET_VOLUME                = b'\x04'
SET_VOLUME                = b'\x05'
GET_MINUTES               = b'\x06'
SET_MINUTES               = b'\x07'

opStrings                 = b'\x7D'
    # STRINGS_SUBCODE
GET_SIZE                  = b'\x01'
ADD                       = b'\x02'
COMPARE                   = b'\x03'
DUPLICATE                 = b'\x05'
VALUE_TO_STRING           = b'\x06'
STRING_TO_VALUE           = b'\x07'
STRIP                     = b'\x08'
NUMBER_TO_STRING          = b'\x09'
SUB                       = b'\x0A'
VALUE_FORMATTED           = b'\x0B'
NUMBER_FORMATTED          = b'\x0C'

opMemory_Write            = b'\x7E'
opMemory_Read             = b'\x7F'
opUI_Flush                = b'\x80'   # UI
opUI_Read                 = b'\x81'
    # UI_READ_SUBCODES
GET_VBATT                 = b'\x01'
GET_IBATT                 = b'\x02'
GET_OS_VERS               = b'\x03'
GET_EVENT                 = b'\x04'
GET_TBATT                 = b'\x05'
GET_IINT                  = b'\x06'
GET_IMOTOR                = b'\x07'
GET_STRING                = b'\x08'
GET_HW_VERS               = b'\x09'
GET_FW_VERS               = b'\x0A'
GET_FW_BUILD              = b'\x0B'
GET_OS_BUILD              = b'\x0C'
GET_ADDRESS               = b'\x0D'
GET_CODE                  = b'\x0E'
KEY                       = b'\x0F'
GET_SHUTDOWN              = b'\x10'
GET_WARNING               = b'\x11'
GET_LBATT                 = b'\x12'
TEXTBOX_READ              = b'\x15'
GET_VERSION               = b'\x1A'
GET_IP                    = b'\x1B'
GET_POWER                 = b'\x1D'
GET_SDCARD                = b'\x1E'
GET_USBSTICK              = b'\x1F'

opUI_Write                = b'\x82'
    # UI_WRITE_SUBCODES
WRITE_FLUSH               = b'\x01'
FLOATVALUE                = b'\x02'
STAMP                     = b'\x03'
PUT_STRING                = b'\x08'
VALUE8                    = b'\x09'
VALUE16                   = b'\x0A'
VALUE32                   = b'\x0B'
VALUEF                    = b'\x0C'
ADDRESS                   = b'\x0D'
CODE                      = b'\x0E'
DOWNLOAD_END              = b'\x0F'
SCREEN_BLOCK              = b'\x10'
TEXTBOX_APPEND            = b'\x15'
SET_BUSY                  = b'\x16'
SET_TESTPIN               = b'\x17'
INIT_RUN                  = b'\x18'
UPDATE_RUN                = b'\x1A'
LED                       = b'\x1B'
POWER                     = b'\x1D'
GRAPH_SAMPLE              = b'\x1E'
TERMINAL                  = b'\x1F'

opUI_Button               = b'\x83'
    # UI_BUTTON_SUBCODES
SHORTPRESS                = b'\x01'
LONGPRESS                 = b'\x02'
WAIT_FOR_PRESS            = b'\x03'
FLUSH                     = b'\x04'
PRESS                     = b'\x05'
RELEASE                   = b'\x06'
GET_HORZ                  = b'\x07'
GET_VERT                  = b'\x08'
PRESSED                   = b'\x09'
SET_BACK_BLOCK            = b'\x0A'
GET_BACK_BLOCK            = b'\x0B'
TESTSHORTPRESS            = b'\x0C'
TESTLONGPRESS             = b'\x0D'
GET_BUMBED                = b'\x0E'
GET_CLICK                 = b'\x0F'

opUI_DRAW                 = b'\x84'
    # UI_DRAW_SUBCODES
UPDATE                    = 0x00
CLEAN                     = b'\x01'
PIXEL                     = b'\x02'
LINE                      = b'\x03'
CIRCLE                    = b'\x04'
TEXT                      = b'\x05'
ICON                      = b'\x06'
PICTURE                   = b'\x07'
VALUE                     = b'\x08'
FILLRECT                  = b'\x09'
RECT                      = b'\x0A'
NOTIFICATION              = b'\x0B'
QUESTION                  = b'\x0C'
KEYBOARD                  = b'\x0D'
BROWSE                    = b'\x0E'
VERTBAR                   = b'\x0F'
INVERSERECT               = b'\x10'
SELECT_FONT               = b'\x11'
TOPLINE                   = b'\x12'
FILLWINDOW                = b'\x13'
SCROLL                    = b'\x14'
DOTLINE                   = b'\x15'
VIEW_VALUE                = b'\x16'
VIEW_UNIT                 = b'\x17'
FILLCIRCLE                = b'\x18'
STORE                     = b'\x19'
RESTORE                   = b'\x1A'
ICON_QUESTION             = b'\x1B'
BMPFILE                   = b'\x1C'
POPUP                     = b'\x1D'
GRAPH_SETUP               = b'\x1E'
GRAPH_DRAW                = b'\x1F'
TEXTBOX                   = b'\x20'

opTimer_Wait              = b'\x85'   # TIMER
opTimer_Ready             = b'\x86'
opTimer_Read              = b'\x87'
opBp0                     = b'\x88'   # VM
opBp1                     = b'\x89'
opBp2                     = b'\x8A'
opBp3                     = b'\x8B'
opBp_Set                  = b'\x8C'
opMath                    = b'\x8D'
opRandom                  = b'\x8E'
opTimer_Read_Us           = b'\x8F'   # TIMER
opKeep_Alive              = b'\x90'   # UI
opCom_Read                = b'\x91'   # COM
    # COM_READ_SUBCODES
COMMAND                   = b'\x0E'

opCom_Write               = b'\x92'
    # COM_WRITE_SUBCODES
REPLY                     = b'\x0E'

opSound                   = b'\x94'   # SOUND
    # SOUND_SUBCODES
BREAK                     = b'\x00'
TONE                      = b'\x01'
PLAY                      = b'\x02'
REPEAT                    = b'\x03'
SERVICE                   = b'\x04'

opSound_Test              = b'\x95'
opSound_Ready             = b'\x96'
opInput_Sample            = b'\x97'
opInput_Device_List       = b'\x98'
opInput_Device            = b'\x99'
    # INPUT_DEVICE_SUBCODES
GET_FORMAT                = b'\x02'
CAL_MINMAX                = b'\x03'
CAL_DEFAULT               = b'\x04'
GET_TYPEMODE              = b'\x05'
GET_SYMBOL                = b'\x06'
CAL_MIN                   = b'\x07'
CAL_MAX                   = b'\x08'
SETUP                     = b'\x09'
CLR_ALL                   = b'\x0A'
GET_RAW                   = b'\x0B'
GET_CONNECTION            = b'\x0C'
STOP_ALL                  = b'\x0D'
GET_NAME                  = b'\x15'
GET_MODENAME              = b'\x16'
SET_RAW                   = b'\x17'
GET_FIGURES               = b'\x18'
GET_CHANGES               = b'\x19'
CLR_CHANGES               = b'\x1A'
READY_PCT                 = b'\x1B'
READY_RAW                 = b'\x1C'
READY_SI                  = b'\x1D'
GET_MINMAX                = b'\x1E'
GET_BUMPS                 = b'\x1F'

opInput_Read              = b'\x9A'
opInput_Test              = b'\x9B'
opInput_Ready             = b'\x9C'
opInput_ReadSI            = b'\x9D'
opInput_ReadExt           = b'\x9E'
opInput_Write             = b'\x9F'
opOutput_Get_Type         = b'\xA0'   # OUTPUT
opOutput_Set_Type         = b'\xA1'
opOutput_Reset            = b'\xA2'
opOutput_Stop             = b'\xA3'
opOutput_Power            = b'\xA4'
opOutput_Speed            = b'\xA5'
opOutput_Start            = b'\xA6'
opOutput_Polarity         = b'\xA7'
opOutput_Read             = b'\xA8'
opOutput_Test             = b'\xA9'
opOutput_Ready            = b'\xAA'
opOutput_Position         = b'\xAB'
opOutput_Step_Power       = b'\xAC'
opOutput_Time_Power       = b'\xAD'
opOutput_Step_Speed       = b'\xAE'
opOutput_Time_Speed       = b'\xAF'
opOutput_Step_Sync        = b'\xB0'
opOutput_Time_Sync        = b'\xB1'
opOutput_Clr_Count        = b'\xB2'
opOutput_Get_Count        = b'\xB3'
opOutput_Prg_Stop         = b'\xB4'

opFile                    = b'\xC0'
    # FILE_SUBCODES
OPEN_APPEND               = b'\x00'
OPEN_READ                 = b'\x01'
OPEN_WRITE                = b'\x02'
READ_VALUE                = b'\x03'
WRITE_VALUE               = b'\x04'
READ_TEXT                 = b'\x05'
WRITE_TEXT                = b'\x06'
CLOSE                     = b'\x07'
LOAD_IMAGE                = b'\x08'
GET_HANDLE                = b'\x09'
MAKE_FOLDER               = b'\x0A'
GET_POOL                  = b'\x0B'
SET_LOG_SYNC_TIME         = b'\x0C'
GET_FOLDERS               = b'\x0D'
GET_LOG_SYNC_TIME         = b'\x0E'
GET_SUBFOLDER_NAME        = b'\x0F'
WRITE_LOG                 = b'\x10'
CLOSE_LOG                 = b'\x11'
GET_IMAGE                 = b'\x12'
GET_ITEM                  = b'\x13'
GET_CACHE_FILES           = b'\x14'
PUT_CACHE_FILE            = b'\x15'
GET_CACHE_FILE            = b'\x16'
DEL_CACHE_FILE            = b'\x17'
DEL_SUBFOLDER             = b'\x18'
GET_LOG_NAME              = b'\x19'
opEN_LOG                  = b'\x1B'
READ_BYTES                = b'\x1C'
WRITE_BYTES               = b'\x1D'
REMOVE                    = b'\x1E'
MOVE                      = b'\x1F'

opArray                   = b'\xC1'
    # ARRAY_SUBCODES
DELETE                    = b'\x00'
CREATE8                   = b'\x01'
CREATE16                  = b'\x02'
CREATE32                  = b'\x03'
CREATEF                   = b'\x04'
RESIZE                    = b'\x05'
FILL                      = b'\x06'
COPY                      = b'\x07'
INIT8                     = b'\x08'
INIT16                    = b'\x09'
INIT32                    = b'\x0A'
INITF                     = b'\x0B'
SIZE                      = b'\x0C'
READ_CONTENT              = b'\x0D'
WRITE_CONTENT             = b'\x0E'
READ_SIZE                 = b'\x0F'

opArray_Write             = b'\xC2'
opArray_Read              = b'\xC3'
opArray_Append            = b'\xC4'
opMemory_Usage            = b'\xC5'
opFilename                = b'\xC6'
    # FILENAME_SUBCODE
EXIST                     = b'\x10'
TOTALSIZE                 = b'\x11'
SPLIT                     = b'\x12'
MERGE                     = b'\x13'
CHECK                     = b'\x14'
PACK                      = b'\x15'
UNPACK                    = b'\x16'
GET_FOLDERNAME            = b'\x17'

opRead8                   = b'\xC8'
opRead16                  = b'\xC9'
opRead32                  = b'\xCA'
opReadf                   = b'\xCB'
opWrite8                  = b'\xCC'
opWrite16                 = b'\xCD'
opWrite32                 = b'\xCE'
opWritef                  = b'\xCF'
opCom_Ready               = b'\xD0'
opCom_Readdata            = b'\xD1'
opCom_Writedata           = b'\xD2'
opCom_Get                 = b'\xD3'
    # COM_GET_SUBCODES
GET_ON_OFF                = b'\x01'
GET_VISIBLE               = b'\x02'
GET_RESULT                = b'\x04'
GET_PIN                   = b'\x05'
SEARCH_ITEMS              = b'\x08'
SEARCH_ITEM               = b'\x09'
FAVOUR_ITEMS              = b'\x0A'
FAVOUR_ITEM               = b'\x0B'
GET_ID                    = b'\x0C'
GET_BRICKNAME             = b'\x0D'
GET_NETWORK               = b'\x0E'
GET_PRESENT               = b'\x0F'
GET_ENCRYPT               = b'\x10'
CONNEC_ITEMS              = b'\x11'
CONNEC_ITEM               = b'\x12'
GET_INCOMING              = b'\x13'
GET_MODE2                 = b'\x14'

opCom_Set                 = b'\xD4'
    # COM_SET_SUBCODES
SET_ON_OFF                = b'\x01'
SET_VISIBLE               = b'\x02'
SET_SEARCH                = b'\x03'
SET_PIN                   = b'\x05'
SET_PASSKEY               = b'\x06'
SET_CONNECTION            = b'\x07'
SET_BRICKNAME             = b'\x08'
SET_MOVEUP                = b'\x09'
SET_MOVEDOWN              = b'\x0A'
SET_ENCRYPT               = b'\x0B'
SET_SSID                  = b'\x0C'
SET_MODE2                 = b'\x0D'

opCom_Test                = b'\xD5'
opCom_Remove              = b'\xD6'
opCom_Writefile           = b'\xD7'
opMailbox_Open            = b'\xD8'
opMailbox_Write           = b'\xD9'
opMailbox_Read            = b'\xDA'
opMailbox_Test            = b'\xDB'
opMailbox_Ready           = b'\xDC'
opMailbox_Close           = b'\xDD'
opTst                     = b'\xDD'
    # TST_SUBCODES
TST_OPEN                  = b'\x0A'
TST_CLOSE                 = b'\x0B'
TST_READ_PINS             = b'\x0C'
TST_WRITE_PINS            = b'\x0D'
TST_READ_ADC              = b'\x0E'
TST_WRITE_UART            = b'\x0F'
TST_READ_UART             = b'\x10'
TST_ENABLE_UART           = b'\x11'
TST_DISABLE_UART          = b'\x12'
TST_ACCU_SWITCH           = b'\x13'
TST_BOOT_MODE2            = b'\x14'
TST_POLL_MODE2            = b'\x15'
TST_CLOSE_MODE2           = b'\x16'
TST_RAM_CHECK             = b'\x17'

# Slots
CURRENT_SLOT              = b'\x21'
GUI_SLOT                  = b'\x00'
USER_SLOT                 = b'\x01'
CMD_SLOT                  = b'\x02'
TERM_SLOT                 = b'\x03'
DEBUG_SLOT                = b'\x04'

# sensor ports
PORT_1                    = b'\x00'
PORT_2                    = b'\x01'
PORT_3                    = b'\x02'
PORT_4                    = b'\x03'
PORT_A_SENSOR             = b'\x10'
PORT_B_SENSOR             = b'\x11'
PORT_C_SENSOR             = b'\x12'
PORT_D_SENSOR             = b'\x13'

# motor ports
PORT_A                    = 1
PORT_B                    = 2
PORT_C                    = 4
PORT_D                    = 8
PORTS_ALL                 = 15

# BUTTONTYPES
NO_BUTTON                 = b'\x00'
UP_BUTTON                 = b'\x01'
ENTER_BUTTON              = b'\x02'
DOWN_BUTTON               = b'\x03'
RIGHT_BUTTON              = b'\x04'
LEFT_BUTTON               = b'\x05'
BACK_BUTTON               = b'\x06'
ANY_BUTTON                = b'\x07'
BUTTONTYPES               = b'\x08'

    # MATHTYPES
EXP                       = b'\x01' #!< e^x r = expf(x)
MOD                       = b'\x02' #!< Modulo r = fmod(x'y)
FLOOR                     = b'\x03' #!< Floor r = floor(x)
CEIL                      = b'\x04' #!< Ceiling r = ceil(x)
ROUND                     = b'\x05' #!< Round r = round(x)
ABS                       = b'\x06' #!< Absolute r = fabs(x)
NEGATE                    = b'\x07' #!< Negate r = 0.0 - x
SQRT                      = b'\x08' #!< Squareroot r = sqrt(x)
LOG                       = b'\x09' #!< Log r = log10(x)
LN                        = b'\x0A' #!< Ln r = log(x)
SIN                       = b'\x0B' #!<
COS                       = b'\x0C' #!<
TAN                       = b'\x0D' #!<
ASIN                      = b'\x0E' #!<
ACOS                      = b'\x0F' #!<
ATAN                      = b'\x10' #!<
MOD8                      = b'\x11' #!< Modulo DATA8 r = x % y
MOD16                     = b'\x12' #!< Modulo DATA16 r = x % y
MOD32                     = b'\x13' #!< Modulo DATA32 r = x % y
POW                       = b'\x14' #!< Exponent r = powf(x,y)
# !< Truncate r = (float)((int)(x * pow(y))) / pow(y)
TRUNC                     = b'\x15'

    # BROWSERTYPES
BROWSE_FOLDERS            = b'\x00' # folders
BROWSE_FOLDS_FILES        = b'\x01' # folders and files
BROWSE_CACHE              = b'\x02' # cached / recent files
BROWSE_FILES              = b'\x03' # files

    # FONTTYPES
NORMAL_FONT               = b'\x00'
SMALL_FONT                = b'\x01'
LARGE_FONT                = b'\x02'
TINY_FONT                 = b'\x03'

    # ICONTYPES
NORMAL_ICON               = b'\x00' # 24x12_Files_Folders_Settings.bmp
SMALL_ICON                = b'\x01'
LARGE_ICON                = b'\x02' # 24x22_Yes_No_OFF_FILEOps.bmp
MENU_ICON                 = b'\x03'
ARROW_ICON                = b'\x04' # 8x12_miniArrows.bmp

    # S_ICON_NO
SICON_CHARGING            = b'\x00'
SICON_BATT_4              = b'\x01'
SICON_BATT_3              = b'\x02'
SICON_BATT_2              = b'\x03'
SICON_BATT_1              = b'\x04'
SICON_BATT_0              = b'\x05'
SICON_WAIT1               = b'\x06'
SICON_WAIT2               = b'\x07'
SICON_BT_ON               = b'\x08'
SICON_BT_VISIBLE          = b'\x09'
SICON_BT_CONNECTED        = b'\x0A'
SICON_BT_CONNVISIB        = b'\x0B'
SICON_WIFI_3              = b'\x0C'
SICON_WIFI_2              = b'\x0D'
SICON_WIFI_1              = b'\x0E'
SICON_WIFI_CONNECTED      = b'\x0F'
SICON_USB                 = b'\x15'

    # N_ICON_NO
ICON_NONE                 = b'\x21'
ICON_RUN                  = b'\x00'
ICON_FOLDER               = b'\x01'
ICON_FOLDER2              = b'\x02'
ICON_USB                  = b'\x03'
ICON_SD                   = b'\x04'
ICON_SOUND                = b'\x05'
ICON_IMAGE                = b'\x06'
ICON_SETTINGS             = b'\x07'
ICON_ONOFF                = b'\x08'
ICON_SEARCH               = b'\x09'
ICON_WIFI                 = b'\x0A'
ICON_CONNECTIONS          = b'\x0B'
ICON_ADD_HIDDEN           = b'\x0C'
ICON_TRASHBIN             = b'\x0D'
ICON_VISIBILITY           = b'\x0E'
ICON_KEY                  = b'\x0F'
ICON_CONNECT              = b'\x10'
ICON_DISCONNECT           = b'\x11'
ICON_UP                   = b'\x12'
ICON_DOWN                 = b'\x13'
ICON_WAIT1                = b'\x14'
ICON_WAIT2                = b'\x15'
ICON_BLUETOOTH            = b'\x16'
ICON_INFO                 = b'\x17'
ICON_TEXT                 = b'\x18'
ICON_QUESTIONMARK         = b'\x1B'
ICON_INFO_FILE            = b'\x1C'
ICON_DISC                 = b'\x1D'
ICON_CONNECTED            = b'\x1E'
ICON_OBP                  = b'\x1F'
ICON_OBD                  = b'\x20'
ICON_OPENFOLDER           = b'\x21'
ICON_BRICK1               = b'\x22'

    # L_ICON_NO
YES_NOTSEL                = b'\x00'
YES_SEL                   = b'\x01'
NO_NOTSEL                 = b'\x02'
NO_SEL                    = b'\x03'
OFF                       = b'\x04'
WAIT_VERT                 = b'\x05'
WAIT_HORZ                 = b'\x06'
TO_MANUAL                 = b'\x07'
WARNSIGN                  = b'\x08'
WARN_BATT                 = b'\x09'
WARN_POWER                = b'\x0A'
WARN_TEMP                 = b'\x0B'
NO_USBSTICK               = b'\x0C'
TO_EXECUTE                = b'\x0D'
TO_BRICK                  = b'\x0E'
TO_SDCARD                 = b'\x0F'
TO_USBSTICK               = b'\x10'
TO_BLUETOOTH              = b'\x11'
TO_WIFI                   = b'\x12'
TO_TRASH                  = b'\x13'
TO_COPY                   = b'\x14'
TO_FILE                   = b'\x15'
CHAR_ERROR                = b'\x16'
COPY_ERROR                = b'\x17'
PROGRAM_ERROR             = b'\x18'
WARN_MEMORY               = b'\x1B'

    # M_ICON_NO
ICON_STAR                 = b'\x00'
ICON_LOCKSTAR             = b'\x01'
ICON_LOCK                 = b'\x02'
ICON_PC                   = b'\x03' # Bluetooth type PC
ICON_PHONE                = b'\x04' # Bluetooth type PHONE
ICON_BRICK                = b'\x05' # Bluetooth type BRICK
ICON_UNKNOWN              = b'\x06' # Bluetooth type UNKNOWN
ICON_FROM_FOLDER          = b'\x07'
ICON_CHECKBOX             = b'\x08'
ICON_CHECKED              = b'\x09'
ICON_XED                  = b'\x0A'

    # A_ICON_NO
ICON_LEFT                 = b'\x01'
ICON_RIGHT                = b'\x02'

    #  BTTYPE
BTTYPE_PC                 = b'\x03' # Bluetooth type PC
BTTYPE_PHONE              = b'\x04' # Bluetooth type PHONE
BTTYPE_BRICK              = b'\x05' # Bluetooth type BRICK
BTTYPE_UNKNOWN            = b'\x06' # Bluetooth type UNKNOWN

    # LEDPATTERN
LED_OFF                   = b'\x00'
LED_GREEN                 = b'\x01'
LED_RED                   = b'\x02'
LED_ORANGE                = b'\x03'
LED_GREEN_FLASH           = b'\x04'
LED_RED_FLASH             = b'\x05'
LED_ORANGE_FLASH          = b'\x06'
LED_GREEN_PULSE           = b'\x07'
LED_RED_PULSE             = b'\x08'
LED_ORANGE_PULSE          = b'\x09'

    # LEDTYPE
LED_ALL                   = b'\x00' # All LEDs
LED_RR                    = b'\x01' # Right red
LED_RG                    = b'\x02' # Right green
LED_LR                    = b'\x03' # Left red
LED_LG                    = b'\x04' # Left green

    # FILETYPE
FILETYPE_UNKNOWN          = b'\x00'
TYPE_FOLDER               = b'\x01'
TYPE_SOUND                = b'\x02'
TYPE_BYTECODE             = b'\x03'
TYPE_GRAPHICS             = b'\x04'
TYPE_DATALOG              = b'\x05'
TYPE_PROGRAM              = b'\x06'
TYPE_TEXT                 = b'\x07'
TYPE_SDCARD               = b'\x10'
TYPE_USBSTICK             = b'\x20'
TYPE_RESTART_BROWSER      = b'\x21'
TYPE_REFRESH_BROWSER      = b'\x22'

    # RESULT
OK                        = b'\x00' # No errors to report
BUSY                      = b'\x01' # Busy - try again
FAIL                      = b'\x02' # Something failed
STOP                      = b'\x04' # Stopped

    # DATA_FORMAT
DATA_8                    = b'\x00' # DATA8 (don't change)
DATA_16                   = b'\x01' # DATA16 (don't change)
DATA_32                   = b'\x02' # DATA32 (don't change)
DATA_F                    = b'\x03' # DATAF (don't change)
DATA_S                    = b'\x04' # Zero terminated string
DATA_A                    = b'\x05' # Array handle
DATA_V                    = b'\x07' # Variable type
DATA_PCT                  = b'\x10' # Percent (used in opINPUT_READEXT)
DATA_RAW                  = b'\x12' # Raw (used in opINPUT_READEXT)
DATA_SI                   = b'\x13' # SI unit (used in opINPUT_READEXT)

    # DEL
DEL_NONE                  = b'\x00' # No delimiter at all
DEL_TAB                   = b'\x01' # Use tab as delimiter
DEL_SPACE                 = b'\x02' # Use space as delimiter
DEL_RETURN                = b'\x03' # Use return as delimiter
DEL_COLON                 = b'\x04' # Use colon as delimiter
DEL_COMMA                 = b'\x05' # Use comma as delimiter
DEL_LINEFEED              = b'\x06' # Use line feed as delimiter
DEL_CRLF                  = b'\x07' # Use return+line feed as delimiter

    # HWTYPE
HW_USB                    = b'\x01'
HW_BT                     = b'\x02'
HW_WIFI                   = b'\x03'

    # ENCRYPT
ENCRYPT_NONE              = b'\x00'
ENCRYPT_WPA2              = b'\x01'


    # MIX
MODE_KEEP                 = b'\x21'
TYPE_KEEP                 = b'\x00'

    # COLOR
RED                       = b'\x00'
GREEN                     = b'\x01'
BLUE                      = b'\x02'
BLANK                     = b'\x03'

    # NXTCOLOR
BLACKCOLOR                = b'\x01'
BLUECOLOR                 = b'\x02'
GREENCOLOR                = b'\x03'
YELLOWCOLOR               = b'\x04'
REDCOLOR                  = b'\x05'
WHITECOLOR                = b'\x06'

    # WARNING
WARNING_TEMP              = b'\x01'
WARNING_CURRENT           = b'\x02'
WARNING_VOLTAGE           = b'\x04'
WARNING_MEMORY            = b'\x08'
WARNING_DSPSTAT           = b'\x10'
WARNING_BATTLOW           = b'\x40'
WARNING_BUSY              = b'\x80'

    # OBJSTAT
RUNNING                   = b'\x10' # Object code is running
WAITING                   = b'\x20' # Object is waiting for final trigger
STOPPED                   = b'\x40' # Object is stopped or not triggered yet
 # Object is halted because a call is in progress
HALTED                    = b'\x80'

    #DEVCMD
DEVCMD_RESET              = b'\x11' # UART device reset
DEVCMD_FIRE               = b'\x11' # UART device fire (ultrasonic)
DEVCMD_CHANNEL            = b'\x12' # UART device channel (IR seeker)

def LCX(value: int) -> bytes:
    """create a LC0, LC1, LC2, LC4, dependent from the value"""
    if type(value) == 'bytes' and len(value) == 1:
        value = struct.unpack('b', value)[0]

    if   value >=    -32 and value <      0:
        return struct.pack('b', 0x3F & (value + 64))
    elif value >=      0 and value <     32:
        return struct.pack('b', value)
    elif value >=   -127 and value <=   127:
        return b'\x81' + struct.pack('<b', value)
    elif value >= -32767 and value <= 32767:
        return b'\x82' + struct.pack('<h', value)
    else:
        return b'\x83' + struct.pack('<i', value)

def LCS(value: str) -> bytes:
    """
    pack a string into a LCS
    """
    return b'\x84' + str.encode(value) + b'\x00'

def LVX(value: int) -> bytes:
    """
    create a LV0, LV1, LV2, LV4, dependent from the value
    """
    if value   <     0:
        raise RuntimeError('No negative values allowed')
    elif value <    32:
        return struct.pack('b', 0x40 | value)
    elif value <   256:
        return b'\xc1' + struct.pack('<b', value)
    elif value < 65536:
        return b'\xc2' + struct.pack('<h', value)
    else:
        return b'\xc3' + struct.pack('<i', value)

def GVX(value: int) -> bytes:
    """create a GV0, GV1, GV2, GV4, dependent from the value"""
    if value   <     0:
        raise RuntimeError('No negative values allowed')
    elif value <    32:
        return struct.pack('<b', 0x60 | value)
    elif value <   256:
        return b'\xe1' + struct.pack('<b', value)
    elif value < 65536:
        return b'\xe2' + struct.pack('<h', value)
    else:
        return b'\xe3' + struct.pack('<i', value)

def port_motor_input(port_output: int) -> bytes:
    """
    get corresponding input motor port (from output motor port)
    """
    if port_output == PORT_A:
        return LCX(16)
    elif port_output == PORT_B:
        return LCX(17)
    elif port_output == PORT_C:
        return LCX(18)
    elif port_output == PORT_D:
        return LCX(19)
    else:
        raise ValueError("port_output needs to be one of the port numbers [1, 2, 4, 8]")

class ForeignReplies:
    """
    foreign replies of the EV3
    """
    def __init__(self):
        self._unwanted = {}

    def put(self, counter: bytes, reply: bytes):
        """
        put a foreign reply to the stack
        """
        if counter in self._unwanted:
            raise ValueError('reply with counter ' + key + ' already exists')
        else:
            self._unwanted[counter] = reply

    def get(self, counter: bytes) -> bytes:
        """
        get a reply from the stack (returns None if there is no)
        and delete reply from the stack
        """
        if counter in self._unwanted:
            reply = self._unwanted[counter]
            del self._unwanted[counter]
            return reply
        else:
            return None

class MessageCounter:
    """
    message counter
    """
    def __init__(self):
        self._cnt = 41
    def next(self):
        if self._cnt < 65535:
            self._cnt += 1
            return self._cnt
        else:
            self._cnt = 42
            return self._cnt
    @property
    def cnt(self):
        """
        actual value of message counter (the last given)
        """
        return self._cnt    

# pylint: disable=too-many-arguments
class EV3:
    """
    object to communicate with a LEGO EV3 using direct commands
    """

    _lock = threading.Lock()

    def __init__(self, protocol: str=None, host: str=None, ev3_obj=None):
        """
        Establish a connection to a LEGO EV3 device

        Arguments (either protocol and host or ev3_obj):
        protocol:
          BLUETOOTH == 'B'
          USB == 'U'
          WIFI == 'W'
        host: mac-address of the LEGO EV3 (f.i. '00:16:53:42:2B:99')
        ev3_obj: an existing EV3 object (its connections will be used)
        """
        assert ev3_obj or protocol, \
            'Either protocol or ev3_obj needs to be given'
        if ev3_obj:
            assert isinstance(ev3_obj, EV3), \
                'ev3_obj needs to be instance of EV3'
            self._protocol = ev3_obj._protocol
            self._device = ev3_obj._device
            self._socket = ev3_obj._socket
            self._foreign = ev3_obj._foreign
            self._msg_cnt = ev3_obj._msg_cnt
        elif protocol:
            assert protocol in [BLUETOOTH, WIFI, USB], \
                'Protocol ' + protocol + 'is not valid'
            self._protocol = None
            self._device = None
            self._socket = None
            if protocol == BLUETOOTH:
                assert host, 'Protocol ' + protocol + 'needs host-id'
                self._connect_bluetooth(host)
            elif protocol == WIFI:
                self._connect_wifi()
            elif protocol == USB:
                self._connect_usb()
            self._foreign = ForeignReplies()
            self._msg_cnt = MessageCounter()
        self._verbosity = 0
        self._sync_mode = STD
        self._return_ops = False

    @property
    def sync_mode(self):
        """
        sync mode (standard, asynchronous, synchronous)

        STD = 0:   Use DIRECT_COMMAND_REPLY if global_mem > 0,
                   wait for reply if there is one.
        ASYNC = 1: Use DIRECT_COMMAND_REPLY if global_mem > 0,
                   never wait for reply (it's the task of the calling program).
        SYNC = 2:  Always use DIRECT_COMMAND_REPLY and wait for reply.

        The general idea is:
        STD:   EV3 device is never blocked,
               control directly comes back.
        ASYNC: EV3 device queues direct commands,
               control directly comes back.
        SYNC:  EV3 device is blocked until direct command is finished.
               control comes back, when direct command is finished               
        """
        return self._sync_mode
    @sync_mode.setter
    def sync_mode(self, value:int):
        if not isinstance(value, int):
            raise ValueError("sync_mode needs to be of type int")
        if not value in [SYNC, ASYNC]:
            raise ValueError("value of sync_mode is invalid")
        self._sync_mode = value

    @property
    def verbosity(self) -> int:
        """
        level of verbosity (prints on stdout).
        """
        return self._verbosity
    @verbosity.setter
    def verbosity(self, value:int):
        if not isinstance(value, int):
            raise ValueError("verbosity needs to be of type int")
        if value < 0 or value > 2:
            raise ValueError("allowed verbosity values are: 0, 1 or 2")
        self._verbosity = value

    def __del__(self):
        """
        closes the connection to the LEGO EV3
        """
        if     self._protocol == BLUETOOTH \
            or self._protocol == WIFI:
            self._socket.close()

    def _connect_bluetooth(self, host: str) -> int:
        """
        Create a socket, that holds a bluetooth-connection to an EV3
        """
        self._socket = socket.socket(socket.AF_BLUETOOTH,
                                     socket.SOCK_STREAM,
                                     socket.BTPROTO_RFCOMM)
        self._socket.connect((host, 1))
        self._protocol = BLUETOOTH
        return 1

    def _connect_wifi(self) -> int:
        """
        Create a socket, that holds a wifi-connection to an EV3
        """

        #pylint: disable=anomalous-backslash-in-string

        # listen on port 3015 for a UDP broadcast from the EV3
        UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDPSock.bind(('', 3015))
        data, addr = UDPSock.recvfrom(67)

        # pick serial number, port, name and protocol
        # from the broadcast message
        matcher = re.search('Serial-Number: (\w*)\s\n' +
                            'Port: (\d{4,4})\s\n' +
                            'Name: (\w+)\s\n' +
                            'Protocol: (\w+)\s\n',
                            data.decode('utf-8'))
        serial_number = matcher.group(1)
        port          = matcher.group(2)
        name          = matcher.group(3)
        protocol      = matcher.group(4)

        # Send an UDP message back to the EV3
        # to make it accept a TCP/IP connection
        UDPSock.sendto(' '.encode('utf-8'), (addr[0], int(port)))
        UDPSock.close()

        # Establish a TCP/IP connection with EV3s address and port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((addr[0], int(port)))

        # Send an unlock message to the EV3 over TCP/IP
        msg = 'GET /target?sn=' + serial_number + 'VMTP1.0\n' + \
              'Protocol: ' + protocol
        self._socket.send(msg.encode('utf-8'))
        reply = self._socket.recv(16).decode('utf-8')
        if not reply.startswith('Accept:EV340'):
            raise RuntimeError('No wifi connection to ' + name + ' established')

        self._protocol = WIFI
        return 1

    def _connect_usb (self) -> int:
        """
        Create a device, that holds an usb-connection to an EV3
        """
        self._device = usb.core.find(idVendor=_ID_VENDOR_LEGO,
                                     idProduct=_ID_PRODUCT_EV3)

        if self._device is None:
            raise RuntimeError("No Lego EV3 found")

        if self._device.is_kernel_driver_active(0) is True:
            self._device.detach_kernel_driver(0)
        self._device.set_configuration()

        # initial read
        self._device.read(_EP_IN, 1024, 100)

        self._protocol = USB
        return 1

    def _complete_direct_cmd(self, ops:bytes,
                             local_mem:int,
                             global_mem:int) -> bytes:
        """
        complete direct command with heading standard parts
        """
        if global_mem > 0  or self._sync_mode == SYNC:
            cmd_type = _DIRECT_COMMAND_REPLY
        else:
            cmd_type = _DIRECT_COMMAND_NO_REPLY
        return b''.join([
            struct.pack('<hh', len(ops) + 5, self._msg_cnt.next()),
            cmd_type,
            struct.pack('<h', local_mem * 1024 + global_mem),
            ops
        ])

    def send_direct_cmd(self, ops: bytes,
                        local_mem: int = 0,
                        global_mem: int = 0) -> bytes:
        """
        Send a direct command to the LEGO EV3

        Arguments:
        ops: holds netto data only (operations), the following fields are added:
          - length: 2 bytes, little endian
          - counter: 2 bytes, little endian
          - type: 1 byte, DIRECT_COMMAND_REPLY or DIRECT_COMMAND_NO_REPLY
          - header: 2 bytes, holds sizes of local and global memory
        
        Keyword Arguments:
        local_mem: size of the local memory
        global_mem: size of the global memory

        Returns: 
            sync_mode = STD: reply (if global_mem > 0) or message counter
            sync_mode = ASYNC: message counter
            sync_mode = SYNC: reply of the LEGO EV3
        """
        cmd = self._complete_direct_cmd(ops, local_mem, global_mem)
        if self._verbosity >= 1:
            now = datetime.datetime.now().strftime('%H:%M:%S.%f')
            print(now + \
                  ' Sent 0x|' + \
                  ':'.join('{:02X}'.format(byte) for byte in cmd[0:2]) + '|' + \
                  ':'.join('{:02X}'.format(byte) for byte in cmd[2:4]) + '|' + \
                  ':'.join('{:02X}'.format(byte) for byte in cmd[4:5]) + '|' + \
                  ':'.join('{:02X}'.format(byte) for byte in cmd[5:7]) + '|' + \
                  ':'.join('{:02X}'.format(byte) for byte in cmd[7:]) + '|' \
            )
        if    self._protocol == BLUETOOTH \
           or self._protocol == WIFI:
            self._socket.send(cmd)
        elif self._protocol == USB:
            self._device.write(_EP_OUT, cmd, 100)
        else:
            raise RuntimeError('No EV3 connected')
        counter = cmd[2:4]
        if  cmd[4:5] == _DIRECT_COMMAND_NO_REPLY or self._sync_mode == ASYNC:
            return counter
        else:
            reply = self.wait_for_reply(counter)
            return reply

    def wait_for_reply(self, counter: bytes) -> bytes:
        """
        Ask the LEGO EV3 for a reply and wait until it is received

        Arguments:
        counter: is the message counter of the corresponding send_direct_cmd
        
        Returns:
        reply to the direct command
        """
        self._lock.acquire()
        if counter:
            reply = self._foreign.get(counter)
            if reply:
                self._lock.release()
                return reply
        while True:
            if    self._protocol == BLUETOOTH \
               or self._protocol == WIFI:
                reply = self._socket.recv(1024)
            else:
                reply = bytes(self._device.read(_EP_IN, 1024, 0))
            global_mem = struct.unpack('<H', reply[:2])[0] - 3
            reply_counter = reply[2:4]
            if self._verbosity >= 1:
                now = datetime.datetime.now().strftime('%H:%M:%S.%f')
                print(now + \
                      ' Recv 0x|' + \
                      ':'.join('{:02X}'.format(byte) for byte in reply[0:2]) + \
                      '|' + \
                      ':'.join('{:02X}'.format(byte) for byte in reply[2:4]) + \
                      '|' + \
                      ':'.join('{:02X}'.format(byte) for byte in reply[4:5]) + \
                      '|', end='')
                if global_mem > 0:
                    dat = ':'.join('{:02X}'.format(byte) for byte in reply[5:global_mem + 5])
                    print(dat + '|')
                else:
                    print()
            if counter != reply_counter:
                self._foreign.put(reply_counter, reply)
            else:
                self._lock.release()
                return reply[:global_mem + 5]

if __name__ == "__main__":
    my_ev3 = EV3(protocol=BLUETOOTH, host='00:16:53:42:2B:99')
    my_ev3.verbosity = 1

    led_sequence = [LED_RED, LED_GREEN, LED_ORANGE, LED_GREEN]
    pos_color = 0

    def next_color():
        global my_ev3, led_sequence, pos_color
        ops = b''.join([
            opUI_Write,
            LED,
            led_sequence[pos_color]
        ])
        my_ev3.send_direct_cmd(ops)
        pos_color += 1
        pos_color %= len(led_sequence)

    print("*** change colors ***")
    for i in range(8):
        next_color()
        time.sleep(1)

    ops = opNop

    print("*** SYNC ***")
    my_ev3.sync_mode = SYNC
    my_ev3.send_direct_cmd(ops)

    print("*** ASYNC ***")
    my_ev3.sync_mode = ASYNC
    counter_first = my_ev3.send_direct_cmd(ops, global_mem=1)
    for i in range(10):
        counter = my_ev3.send_direct_cmd(ops, global_mem=1)
    my_ev3.wait_for_reply(counter)
    my_ev3.wait_for_reply(counter_first)
    print("*** finished ***")
