# module to read or generate Reyleigh Distribution winddata
import math
class windData:
    def __init__(self,type_windData,v_max,v_m,n):
        self.type_windData = type_windData
        self.v_max = v_max # max wind velocity
        self.v_m = v_m # mean wind velocity
        self.n = n # number of intervals 

    # Rayleigh distribution
    def Reyleigh(self):
        pi = 3.1415926
        dv = self.v_max/self.n
        const = pi/2*dv**2/self.v_m**2 # constant in the distribution
        pdf = []
        for k in range(self.n):
            idx = k+1 # k starts from 0, the first interval
            v_exp = -pi/4 * idx**2 * dv**2/self.v_m**2
            v_const = idx * const
            pdf_k = v_const*math.exp(v_exp)

            pdf.append(pdf_k)

        return pdf
    def v_dis(self):
        dv = self.v_max/self.n
        v_data = []
        for k in range(self.n):
            vk = k*dv
            v_data.append(vk)
        return v_data

wind = windData(1,20,7,20)
pdf = wind.Reyleigh()
v_data = wind.v_dis()
print (pdf)
print (v_data)
total = sum(pdf)
print (total)
