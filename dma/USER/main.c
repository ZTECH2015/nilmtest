#include "sys.h"
#include "delay.h"
#include "usart.h"
#include "led.h" 
#include "dma.h"
#include "adc.h"


//ALIENTEK 探索者STM32F407开发板 实验23
//DMA 实验-库函数版本  
//技术支持：www.openedv.com
//淘宝店铺：http://eboard.taobao.com  
//广州市星翼电子科技有限公司  
//作者：正点原子 @ALIENTEK


#define SEND_BUF_SIZE 4	//发送数据长度,最好等于sizeof(TEXT_TO_SEND)+2的整数倍.

u8 SendBuff[SEND_BUF_SIZE];	//发送数据缓冲区
//const u8 TEXT_TO_SEND[]={0x00, 0x01, 0x02, 0x03};	 

  
int main(void)
{	
	u16 i;
	u16 adcx;
	float temp;
	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);//设置系统中断优先级分组2
	delay_init(168);     //初始化延时函数
	uart_init(115200);	//初始化串口波特率为115200
 	MYDMA_Config(DMA2_Stream7,DMA_Channel_4,(u32)&USART1->DR,(u32)SendBuff,SEND_BUF_SIZE);//DMA2,STEAM7,CH4,外设为串口1,存储器为SendBuff,长度为:SEND_BUF_SIZE.     	 		 
 	Adc_init();
	while(1)
	{   
		for(i=0;i<SEND_BUF_SIZE;i++)
		{
			adcx=Get_Adc_Average(ADC_Channel_5,20);//获取通道5的转换值，20次取平均
			temp=(float)adcx*(3.3/4096);          //获取计算后的带小数的实际电压值，比如3.1111
			adcx = temp;
			temp-=adcx;
			temp*=1000;
			SendBuff[i]=adcx;   	   
	    }
      	USART_DMACmd(USART1,USART_DMAReq_Tx,ENABLE);  //使能串口1的DMA发送     
		MYDMA_Enable(DMA2_Stream7,SEND_BUF_SIZE);     //开始一次DMA传输！	  
		//等待DMA传输完成，此时我们来做另外一些事，点灯
		//实际应用中，传输数据期间，可以执行另外的任务
	    while(1)
	    {
			if(DMA_GetFlagStatus(DMA2_Stream7,DMA_FLAG_TCIF7)!=RESET)//等待DMA2_Steam7传输完成
			{ 
				DMA_ClearFlag(DMA2_Stream7,DMA_FLAG_TCIF7);//清除DMA2_Steam7传输完成标志
				break; 
	        }
	    }			    
		}
		delay_ms(100);	   		    
}

