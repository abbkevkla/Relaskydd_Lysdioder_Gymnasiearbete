from fpioa_manager import fm
from machine import UART
from board import board_info

fm.register(board_info.PIN15, fm.fpioa.UART1_TX, force=True)
fm.register(board_info.PIN17, fm.fpioa.UART1_RX, force=True)
# fm.register(board_info.PIN9, fm.fpioa.UART2_TX, force=True)
# fm.register(board_info.PIN10, fm.fpioa.UART2_RX, force=True)

uart_A = UART(UART.UART1, 9600, 8, None, 1, timeout=2000, read_buf_len=4096)
# uart_B = UART(UART.UART2, 115200,8,0,0, timeout=1000, read_buf_len=4096)
write_str = 'rgyooyyygrrggyy\n'
while True:
    data = uart_A.read()
    if data:
        uart_A.write(write_str)
        data = ""

uart_A.deinit()

del uart_A
