import Adafruit_MCP3008

class adc:
    
    V_ref = 5.0
    V_max = 4.5
    V_min = 0.5
    P_base = 14.7 #atmospheric psi
    P_max = 3000.0
    bits = 10
    
    def __init__(self, clock, d_out, d_in, cs):
        self.mcp = Adafruit_MCP3008.MCP3008(clk=clock, cs=cs, miso=d_out, mosi=d_in)
        
    def get_pressure(self, channel):
        V_out = self.get_voltage(channel);
        P_value = (V_out - adc.V_min)
        P_value *= (adc.P_max / (adc.V_max - adc.V_min))
        return P_value
    
    def get_voltage(self, channel):
        bit_value = self.mcp.read_adc(channel)
        V_out = (adc.V_ref/ (2**adc.bits - 1)) * bit_value
        return V_out