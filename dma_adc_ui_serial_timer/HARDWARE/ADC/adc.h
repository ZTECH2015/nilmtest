#ifndef __ADC_H
#define __ADC_H	
#include "sys.h" 
//////////////////////////////////////////////////////////////////////////////////	 
//本程序只供学习使用，未经作者许可，不得用于其它任何用途
//ALIENTEK STM32F407开发板
//ADC 驱动代码	   
//正点原子@ALIENTEK
//技术论坛:www.openedv.com
//创建日期:2014/5/6
//版本：V1.0
//版权所有，盗版必究。
//Copyright(C) 广州市星翼电子科技有限公司 2014-2024
//All rights reserved									  
////////////////////////////////////////////////////////////////////////////////// 	 
	
#define ADC_CH5  		5 		 	//通道5	   	    
	   									   
void Adc_Init(void); 				//ADC通道初始化
u16  Get_Adc(void); 				//获得某个通道值
void GPIO_Configuration(void);
void ADC_Configuration(void);
static void DMA_Configuration(void);
void NVIC_Configuration(void);
#endif 















