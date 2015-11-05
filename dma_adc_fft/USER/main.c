#include "sys.h"
#include "delay.h"
#include "usart.h"
#include "led.h" 
#include "dma.h"
#include "adc.h"
#include "arm_math.h"  


//ALIENTEK 探索者STM32F407开发板 实验23
//DMA 实验-库函数版本  
//技术支持：www.openedv.com
//淘宝店铺：http://eboard.taobao.com  
//广州市星翼电子科技有限公司  
//作者：正点原子 @ALIENTEK
/* Private typedef -----------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/
#define ADC_CDR_ADDRESS    ((uint32_t)0x40012308)

/* Private macro -------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/
#define BUFFERSIZE    2048
__IO uint32_t ADCTripleConvertedValue[BUFFERSIZE];

#define SEND_BUF_SIZE 2048	//发送数据长度,最好等于sizeof(TEXT_TO_SEND)+2的整数倍.
#define DATA_SIZE 4096 // define data size which is half of buffer size
float fft_outputbuf[DATA_SIZE];

float SendBuff[SEND_BUF_SIZE];	//发送数据缓冲区
float Data2SendBuff[SEND_BUF_SIZE];
float Data[DATA_SIZE*2]; //fft input size is data size *2
//const u8 TEXT_TO_SEND[]={0x00, 0x01, 0x02, 0x03};	 
uint8_t *BufferReady;
uint8_t *DataReady;
  
int main(void)
{	
	u16 i;
	
	NVIC_Configuration();
	//NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);//设置系统中断优先级分组2
	delay_init(168);     //初始化延时函数
	uart_init(460800);	//初始化串口波特率为115200
 	MYDMA_Config(DMA2_Stream7,DMA_Channel_4,(u32)&USART1->DR,(u32)SendBuff,SEND_BUF_SIZE);//DMA2,STEAM7,CH4,外设为串口1,存储器为SendBuff,长度为:SEND_BUF_SIZE.     	 		 
 	Adc_Init();
	ADC_SoftwareStartConv(ADC1);
	BufferReady = NULL;
	DataReady = NULL;
	while(1)
	{   
			while(!DataReady) // Wait for DMA interrupt to signal next available block
				__WFI();
			for(i=0;i<SEND_BUF_SIZE;i++){
				SendBuff[i] = Data2SendBuff[i];
			}
			DataReady = NULL;
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
}


void  Adc_Init(void)
{    
	ADC_InitTypeDef       ADC_InitStructure;
	ADC_CommonInitTypeDef ADC_CommonInitStructure;
	DMA_InitTypeDef       DMA_InitStructure;
	GPIO_InitTypeDef      GPIO_InitStructure;
	/* Enable peripheral clocks */
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_DMA2 | RCC_AHB1Periph_GPIOC, ENABLE);
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_ADC1 | RCC_APB2Periph_ADC2 | RCC_APB2Periph_ADC3, ENABLE);
	/* Configure ADC Channel 12 pin as analog input */ 
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_2;
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AN;
	GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_NOPULL ;
	GPIO_Init(GPIOC, &GPIO_InitStructure);
 
	RCC_APB2PeriphResetCmd(RCC_APB2Periph_ADC1,ENABLE);	//ADC1复位
	RCC_APB2PeriphResetCmd(RCC_APB2Periph_ADC1,DISABLE);	//复位结束	 
	RCC_APB2PeriphResetCmd(RCC_APB2Periph_ADC2,ENABLE);	//ADC2复位
	RCC_APB2PeriphResetCmd(RCC_APB2Periph_ADC2,DISABLE);	//复位结束	 
	RCC_APB2PeriphResetCmd(RCC_APB2Periph_ADC3,ENABLE);	//ADC3复位
	RCC_APB2PeriphResetCmd(RCC_APB2Periph_ADC3,DISABLE);	//复位结束	 
 
	/* DMA2 Stream0 channel0 configuration */
	DMA_InitStructure.DMA_Channel = DMA_Channel_0;  
	DMA_InitStructure.DMA_PeripheralBaseAddr = (uint32_t)ADC_CDR_ADDRESS;
	DMA_InitStructure.DMA_Memory0BaseAddr = (uint32_t)&ADCTripleConvertedValue;
	DMA_InitStructure.DMA_DIR = DMA_DIR_PeripheralToMemory;
	DMA_InitStructure.DMA_BufferSize = BUFFERSIZE;
	DMA_InitStructure.DMA_PeripheralInc = DMA_PeripheralInc_Disable;
	DMA_InitStructure.DMA_MemoryInc = DMA_MemoryInc_Enable;
	DMA_InitStructure.DMA_PeripheralDataSize = DMA_PeripheralDataSize_Word;
	DMA_InitStructure.DMA_MemoryDataSize = DMA_MemoryDataSize_Word;
	DMA_InitStructure.DMA_Mode = DMA_Mode_Circular;
	DMA_InitStructure.DMA_Priority = DMA_Priority_High;
	DMA_InitStructure.DMA_FIFOMode = DMA_FIFOMode_Disable;         
	DMA_InitStructure.DMA_FIFOThreshold = DMA_FIFOThreshold_HalfFull;
	DMA_InitStructure.DMA_MemoryBurst = DMA_MemoryBurst_Single;
	DMA_InitStructure.DMA_PeripheralBurst = DMA_PeripheralBurst_Single;
	DMA_Init(DMA2_Stream0, &DMA_InitStructure);
	
	/* Enable DMA Stream Half / Transfer Complete interrupt */
  DMA_ITConfig(DMA2_Stream0, DMA_IT_TC | DMA_IT_HT, ENABLE);

	/* DMA2_Stream0 enable */
	DMA_Cmd(DMA2_Stream0, ENABLE);	

	/* ADC Common configuration *************************************************/
	ADC_CommonInitStructure.ADC_Mode = ADC_TripleMode_Interl;
	ADC_CommonInitStructure.ADC_TwoSamplingDelay = ADC_TwoSamplingDelay_5Cycles;
	ADC_CommonInitStructure.ADC_DMAAccessMode = ADC_DMAAccessMode_2;  
	ADC_CommonInitStructure.ADC_Prescaler = ADC_Prescaler_Div2; 
	ADC_CommonInit(&ADC_CommonInitStructure);

	/* ADC1 regular channel 12 configuration ************************************/
	ADC_InitStructure.ADC_Resolution = ADC_Resolution_12b;
	ADC_InitStructure.ADC_ScanConvMode = DISABLE;
	ADC_InitStructure.ADC_ContinuousConvMode = ENABLE;
	ADC_InitStructure.ADC_ExternalTrigConvEdge = ADC_ExternalTrigConvEdge_None;
	ADC_InitStructure.ADC_DataAlign = ADC_DataAlign_Right;
	ADC_InitStructure.ADC_NbrOfConversion = 1;
	ADC_Init(ADC1, &ADC_InitStructure);

	ADC_RegularChannelConfig(ADC1, ADC_Channel_12, 1, ADC_SampleTime_3Cycles);

	/* Enable ADC1 DMA */
	ADC_DMACmd(ADC1, ENABLE);

	/* ADC2 regular channel 12 configuration ************************************/
	ADC_Init(ADC2, &ADC_InitStructure);
	/* ADC2 regular channel12 configuration */ 
	ADC_RegularChannelConfig(ADC2, ADC_Channel_12, 1, ADC_SampleTime_3Cycles);

	/* ADC3 regular channel 12 configuration ************************************/
	ADC_Init(ADC3, &ADC_InitStructure); 

	/* ADC3 regular channel12 configuration *************************************/
	ADC_RegularChannelConfig(ADC3, ADC_Channel_12, 1, ADC_SampleTime_3Cycles);

	/* Enable DMA request after last transfer (multi-ADC mode) ******************/
	ADC_MultiModeDMARequestAfterLastTransferCmd(ENABLE);

	/* Enable ADC1 **************************************************************/
	ADC_Cmd(ADC1, ENABLE);

	/* Enable ADC2 **************************************************************/
	ADC_Cmd(ADC2, ENABLE);

	/* Enable ADC3 **************************************************************/
	ADC_Cmd(ADC3, ENABLE);
 
}			

void DMA2_Stream0_IRQHandler(void)
{
	int i;
	arm_cfft_radix4_instance_f32 scfft;
	arm_cfft_radix4_init_f32(&scfft,DATA_SIZE,0,1);
	if(DataReady){
		DMA_ClearITPendingBit(DMA2_Stream0, DMA_IT_HTIF0);
		return;
	}
	/* Test on DMA Stream Half Transfer interrupt */
  if(DMA_GetITStatus(DMA2_Stream0, DMA_IT_HTIF0))
  {
    /* Clear DMA Stream Half Transfer interrupt pending bit */
    DMA_ClearITPendingBit(DMA2_Stream0, DMA_IT_HTIF0);
		
		for(i=0;i<DATA_SIZE/2;i++)
			{
				Data[2*i]=ADCTripleConvertedValue[i] * 3.3 /4096 - 1.6;   
				Data[2*i+1] = 0;
				}
    // Add code here to process first half of buffer (ping)
    //BufferReady = (uint8_t *)&ADCTripleConvertedValue[0];
  }
	
  /* Test on DMA Stream Transfer Complete interrupt */
  if(DMA_GetITStatus(DMA2_Stream0, DMA_IT_TCIF0))
  {
    /* Clear DMA Stream Transfer Complete interrupt pending bit */
    DMA_ClearITPendingBit(DMA2_Stream0, DMA_IT_TCIF0);
		
		for(i=DATA_SIZE/2;i<DATA_SIZE;i++)
			{
				Data[2*i]=ADCTripleConvertedValue[i] * 3.3 /4096 - 1.6;   
				Data[2*i+1] = 0;  	   
				}
    // Add code here to process second half of buffer (pong)
		arm_cfft_radix4_f32(&scfft,Data);
		arm_cmplx_mag_f32(Data,fft_outputbuf,DATA_SIZE);
		for(i=0;i<SEND_BUF_SIZE;i++){
			Data2SendBuff[i] = fft_outputbuf[i];
		}
    DataReady = (uint8_t *)&Data2SendBuff[0];
  }
}

