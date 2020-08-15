# -*- coding:utf-8 -*-
import time
import wiringpi2 as wiringpi

PWM18 =18

interval = float( 2.5 )
upper_pulse = float( 2.4 )
under_pulse = float( 0.5 )
duty_range = 1024
duty_ratio = upper_pulse /interval
hz = 1 /( interval *0.001 )
clock = int( 18750 /hz )
duty = int( duty_ratio *duty_range )

print("pin = ", PWM18, " interval[ms] = ", interval, " upper_pulse[ms] = ", upper_pulse )
print("clock = ", clock, " duty=", duty, " duty_ratio=", duty_ratio )
# 初期設定
wiringpi.wiringPiSetupGpio()
wiringpi.pinMode( PWM18, wiringpi.GPIO.PWM_OUTPUT )
wiringpi.pwmSetMode( wiringpi.GPIO.PWM_MODE_MS )

# ClockとDutyを設定してPWMを生成する
wiringpi.pwmSetClock( clock )
wiringpi.pwmWrite( PWM18, duty )
wiringpi.pwmSetRange(duty_range)

#max min値を計算
min_duty=int((under_pulse /interval) *duty_range *1.1)
max_duty=int((upper_pulse -under_pulse) /interval *duty_range +min_duty *0.9)
print("min_duty = ", min_duty, " max_duty=", max_duty)

value = min_duty

def DagToVal(dag):
    par_dag = (max_duty -min_duty) /180.0
    return int(dag *par_dag +min_duty)

##########################################
import math
posi =0 #初期点
def s_shaped_acceleration(posi, Arrival_pt):
#s-sec:S字加速時間 sec:トータル時間　leng:移動距離
    sleep_sec =0.01
    s_rate =1.0                     #制御単位sec
    accel_len =20               #加速量
    reverse_flg = 1 if posi < Arrival_pt else -1   #反転動作
    motion_len = Arrival_pt -posi #移動量

    dist_div= 1 /s_rate                 #細分係数
    accel_div = int(dist_div *accel_len) #細分加速
    motion_div = dist_div *motion_len   #細分定速
    motion_div =abs(motion_div)
    cons_div  =int(motion_div -accel_div *2)

    cons_len =(math.sqrt(2) /2) /accel_div    #按分距離
    integ_len =abs(1 -math.sqrt(2)) *2 +cons_len *cons_div #積分距離
    dist_integ =motion_len /integ_len# *reverse_flg

    for s_i in range (0, accel_div ) :
        degrees1 = math.sqrt(math.pow(s_i /accel_div, 2 ) +1) -1
        degrees1 *=dist_integ
        degrees_motion =degrees1 +posi
        
        s_value =DagToVal(degrees_motion)
        print ("value:",s_value)
        wiringpi.pwmWrite(PWM18, s_value)
        time.sleep( sleep_sec )
        
    degrees_sum = degrees_motion
    degrees1 =0
    for i in range(1 ,cons_div):
        degrees1 = i *cons_len
        degrees1 *=dist_integ
        degrees_motion =degrees1 +degrees_sum
        
        s_value =DagToVal( degrees_motion)
        print ("value:", s_value)
        wiringpi.pwmWrite(PWM18, s_value)
        time.sleep( sleep_sec )
        
    degrees_sum += degrees1

    for i in range(accel_div ,0 ,-1):
        degrees1 = math.sqrt(2)-math.sqrt(math.pow(( i /accel_div),2) +1)
        degrees1 *=dist_integ
        degrees_motion =degrees1 +degrees_sum
        
        s_value =DagToVal( degrees_motion)
        print ("value:", s_value)
        wiringpi.pwmWrite(PWM18, s_value)
        time.sleep( sleep_sec)

    posi =degrees_motion 


#######################################################

if __name__ == "__main__":
    try:

        while True:
            s_shaped_acceleration(0, 120)
            time.sleep( 1 )
            s_shaped_acceleration(120, 0)
            time.sleep( 1 )
            wiringpi.pwmWrite(PWM18, value)
            time.sleep( 0.05)
            value +=1
            if value >= max_duty :
                time.sleep( 1 )

                value =DagToVal(0)
                print ("value:", value)
                wiringpi.pwmWrite(PWM18, value)
                time.sleep( 1 )
                
                value =DagToVal(180)
                print ("value:", value)
                wiringpi.pwmWrite(PWM18, value)
                time.sleep( 1 )
                
                value =DagToVal(90)
                print ("value:",value)
                wiringpi.pwmWrite(PWM18, value)
                time.sleep( 1 )

                value =min_duty
                wiringpi.pwmWrite(PWM18, value)
                print ("Svalue:", value)
                time.sleep( 1)

            print ("Svalue:", value)
    except KeyboardInterrupt:
        wiringpi.pinMode(PWM18, wiringpi.GPIO.INPUT)
        pass
