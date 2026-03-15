
#include "dht.h"
#include <MQUnifiedsensor.h>
#include <string.h>

#define DHT11_PIN               2
#define MIC_PIN                 A2
#define Board                   ("Arduino UNO")
#define Voltage_Resolution      (5)
#define ADC_Bit_Resolution      (10)
#define GAS_PIN                 (A0)  
#define Type_gas                ("MQ-2")
#define RatioMQ2CleanAir        (9.83) 
#define CO_PIN                  (A4)  
#define Type_CO                 ("MQ-9") 
#define RatioMQ9CleanAir        (9.6)

MQUnifiedsensor MQ9(Board, Voltage_Resolution, ADC_Bit_Resolution, CO_PIN, Type_CO);
MQUnifiedsensor MQ2(Board, Voltage_Resolution, ADC_Bit_Resolution, GAS_PIN, Type_gas);

dht DHT;

int check=0,noise=0;
double long start=0,actual=0; 
void setup(){
  Serial.begin(115200);

  MQ9.setRegressionMethod(1); 
  MQ9.setA(599.65); MQ9.setB(-2.244);
  MQ9.init();
  MQ9.setRL(1);
  MQ9.setR0(1.37);
  
  MQ2.setRegressionMethod(1);
  MQ2.setA(574.25); MQ2.setB(-2.222);
  MQ2.init();
  MQ2.setRL(4.7);
  MQ2.setR0(7.03);

  pinMode(MIC_PIN,INPUT);
  while(!Serial);
  
}

void loop(){
  
  start=millis();
  while(1){
    actual=millis();
    
    if(analogRead(MIC_PIN)>64)noise=1;
    
    if(((float)actual-start)/1000>=5.0){
      
      start=actual;
      
      MQ9.update();
      MQ2.update(); 
      float CO = ceil(MQ9.readSensor(false,0)); 
      float gasoline=ceil(MQ2.readSensor(false, 0));
      check = DHT.read11(DHT11_PIN);
      Serial.println(String(CO)+"|"+String(gasoline)+"|"+String(noise)+"|"+String(DHT.humidity)+"|"+String(DHT.temperature));
      
      noise=0;
      
      
    }
  }
}

