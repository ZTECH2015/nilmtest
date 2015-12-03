#include "sys.h"
#include "delay.h"
#include "usart.h"
#include "led.h" 
#include "dma.h"
#include "adc.h"
#include "arm_math.h"  
#include "timer.h"
#include <math.h>


/* Private typedef -----------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/

/* Private macro -------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/
#define DATA_SIZE 1024 // define data size which is half of buffer size
#define DOWN_SAMPLE 8 // define data size which is half of buffer size
#define ONELOOP_DATA_SIZE 64 // define ONE LOOP data size
#define LOOP_SIZE DATA_SIZE/ONELOOP_DATA_SIZE // define LOOP size
#define SEND_BUF_SIZE LOOP_SIZE*4+5	//发送数据长度,最好等于sizeof(TEXT_TO_SEND)的整数倍.
#define BUF_TOL 48
float SendBuff[SEND_BUF_SIZE+BUF_TOL];	//发送数据缓冲区
float Data_v[DATA_SIZE]; //voltage data
float Data_c[DATA_SIZE]; //current data
float Data_p_single[LOOP_SIZE]; //active power data in one cycle
float Data_q_single[LOOP_SIZE]; //reactive power data in one cycle
float Data_v_max[LOOP_SIZE]; //max voltage data in one cycle
float Data_c_max[LOOP_SIZE]; //max current data in one cycle
float Data_max[ONELOOP_DATA_SIZE]; //max current data in one cycle
float fft_outputbuf[DATA_SIZE];
float fft_inputbuf[DATA_SIZE*2];

float time_count;
float t0;
float t1;
uint8_t first;
uint32_t uart_verify;
//const u8 TEXT_TO_SEND[]={0x00, 0x01, 0x02, 0x03};	 
int DataReady;
u8 timeout;// the number of overflow in timer

  
int main(void)
{	
	u16 i;
	u16 j;
	float dummy;
	float u_ave;
	float c_ave;
	arm_cfft_radix4_instance_f32 scfft;
	float test_data0;
	float test_data1;	
	float test_data00=0;
	float test_data11=0;
	float coef_tol = 1.5;
	uart_verify=0;
	delay_init(168);     //初始化延时函数
	uart_init(460800);	//初始化串口波特率为115200
 	MYDMA_Config(DMA2_Stream7,DMA_Channel_4,(u32)&USART1->DR,(u32)SendBuff,(SEND_BUF_SIZE)*4+BUF_TOL*4);//DMA2,STEAM7,CH4,外设为串口1,存储器为SendBuff,长度为:SEND_BUF_SIZE.  
	RCC_Configuration();
	
	GPIO_Configuration();
 
  NVIC_Configuration();
 
  TIM2_Configuration();

  DMA_Configuration();
 
  ADC_Configuration();
	
	ADC_SoftwareStartConv(ADC1);
	
	arm_cfft_radix4_init_f32(&scfft,DATA_SIZE,0,1);
	
	DataReady = 0;
	TIM3_Int_Init(65535,84-1); 
	TIM_SetCounter(TIM3,0);
	timeout = 0;
	
	while(1)
	{   
			while(!DataReady); // Wait for DMA interrupt to signal next available block
				//__WFI();
			
			time_count= TIM_GetCounter(TIM3)+(u32)timeout*65536;
			u_ave = 0;
			c_ave = 0;
			for(i=0;i<DATA_SIZE;i++)
			{
				if((i==0) && (fabs(Data_c[i+1] - Data_c[i])>fabs(Data_c[i+2] - Data_c[i+1])*coef_tol))
				{
					Data_c[i] = Data_c[i+1];
				}
				else
				{
					if((i == DATA_SIZE-1)&&(fabs(Data_c[i] - Data_c[i-1])>fabs(Data_c[i-1] - Data_c[i-2])*coef_tol))
					{
						Data_c[i] = Data_c[i-1];
					}
					else
					{
						if((fabs(Data_c[i] - Data_c[i-1])>fabs(Data_c[i-1] - Data_c[i-2])*coef_tol)&&(fabs(Data_c[i+1] - Data_c[i])>fabs(Data_c[i+2] - Data_c[i+1])*coef_tol))
						{
							Data_c[i] = (Data_c[i-1]+Data_c[i+1])/2;
						}
					}
				}
			}
			for(i=0;i<DATA_SIZE;i++)
			{
				u_ave = u_ave + Data_v[i];
				c_ave = c_ave + Data_c[i];
			}
			u_ave = u_ave / DATA_SIZE;
			c_ave = c_ave / DATA_SIZE;
			for(i=0;i<DATA_SIZE;i++)
			{
				Data_v[i] = Data_v[i] - u_ave;
				Data_c[i] = Data_c[i] - c_ave;
				fft_inputbuf[2*i] = Data_c[i];
				fft_inputbuf[2*i+1] = 0;
			}
			for(i=0;i<LOOP_SIZE;i++)
			{
				for(j=0;j<ONELOOP_DATA_SIZE;j++)
				{
					dummy = fabs(Data_c[i*ONELOOP_DATA_SIZE+j]*Data_v[i*ONELOOP_DATA_SIZE+j]);
					if(j == 0)
					{
						Data_p_single[i] = dummy;
						Data_v_max[i] = fabs(Data_v[i*ONELOOP_DATA_SIZE+j]);
						Data_c_max[i] = fabs(Data_c[i*ONELOOP_DATA_SIZE+j]);
					}
					else
					{
						if(Data_p_single[i] < dummy)
						{
							Data_p_single[i] = dummy;
						}
						dummy = fabs(Data_v[i*ONELOOP_DATA_SIZE+j]);
						if(Data_v_max[i]<dummy)
						{
							Data_v_max[i] = dummy;
						}
						dummy = fabs(Data_c[i*ONELOOP_DATA_SIZE+j]);
						if(Data_c_max[i] < dummy)
						{
							Data_c_max[i] = dummy;
						}
					}
				}
				SendBuff[i] = Data_v_max[i];
				SendBuff[LOOP_SIZE+i] = Data_c_max[i];
				Data_p_single[i] = Data_p_single[i]/sqrt(2);
				SendBuff[2*LOOP_SIZE+i] = Data_p_single[i];
				SendBuff[3*LOOP_SIZE+i] = sqrt(pow(Data_v_max[i]*Data_c_max[i]/sqrt(2),2) - pow(Data_p_single[i],2));
			}
			time_count= TIM_GetCounter(TIM3)+(u32)timeout*65536;
			arm_cfft_radix4_f32(&scfft,fft_inputbuf);
			arm_cmplx_mag_f32(fft_inputbuf,fft_outputbuf,DATA_SIZE);
			for(i=0;i<SEND_BUF_SIZE-4*LOOP_SIZE;i++)
			{
				SendBuff[4*LOOP_SIZE+i] = fft_outputbuf[DATA_SIZE*(i+1)/ONELOOP_DATA_SIZE]/DATA_SIZE/2;
			}
			for(i=SEND_BUF_SIZE;i<SEND_BUF_SIZE+BUF_TOL;i++)
			{
				SendBuff[i] = 0;
			}
//			for(i=0;i<DATA_SIZE;i++)
//			{
//				if(i == 0)
//				{
//					test_data0 = Data_v[i];
//					test_data1 = Data_c[i];
//				}
//				else
//				{
//					test_data0 = test_data0 + Data_v[i];
//					test_data1 = test_data1 + Data_c[i];
//				}
//				//SendBuff[i] = Data_c[i];
//				//SendBuff[DATA_SIZE+i] = Data_v[i];
//			}
//			test_data0 = test_data0 / DATA_SIZE;
//			test_data1 = test_data1 / DATA_SIZE;
//			test_data00 = (test_data00+test_data0)/2;
//			test_data11 = (test_data11+test_data1)/2;
			DataReady = 0;
			time_count= TIM_GetCounter(TIM3)+(u32)timeout*65536;
			USART_DMACmd(USART1,USART_DMAReq_Tx,ENABLE);  //使能串口1的DMA发送   
			if(uart_verify)
			{
				MYDMA_Enable(DMA2_Stream7,SEND_BUF_SIZE*4+BUF_TOL*4);     //开始一次DMA传输！	  
				while(1)
				{
				if(DMA_GetFlagStatus(DMA2_Stream7,DMA_FLAG_TCIF7)!=RESET)//等待DMA2_Steam7传输完成
				{ 
					DMA_ClearFlag(DMA2_Stream7,DMA_FLAG_TCIF7);//清除DMA2_Steam7传输完成标志
					break; 
						}
				}
				uart_verify = 0;
			}
			time_count= TIM_GetCounter(TIM3)+(u32)timeout*65536;
			//time_count = time_count;		
			}   	
}

/**************************************************************************************/
 
void RCC_Configuration(void)
{
  RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_DMA2, ENABLE);
  RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOC, ENABLE);
  RCC_APB2PeriphClockCmd(RCC_APB2Periph_ADC1, ENABLE);
  RCC_APB2PeriphClockCmd(RCC_APB2Periph_ADC2, ENABLE);
  RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM2, ENABLE);
}
 
/**************************************************************************************/
 
void GPIO_Configuration(void)
{
  GPIO_InitTypeDef GPIO_InitStructure;
 
  /* ADC Channel 10 -> PC0
     ADC Channel 11 -> PC1
  */
 
  GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0 | GPIO_Pin_1;
  GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AN;
  GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_NOPULL ;
  GPIO_Init(GPIOC, &GPIO_InitStructure);
}
 
/**************************************************************************************/
void ADC_Configuration(void)
{
  ADC_CommonInitTypeDef ADC_CommonInitStructure;
  ADC_InitTypeDef ADC_InitStructure;
 
  /* ADC Common Init */
  ADC_CommonInitStructure.ADC_Mode = ADC_DualMode_RegSimult;
  ADC_CommonInitStructure.ADC_Prescaler = ADC_Prescaler_Div2;
  ADC_CommonInitStructure.ADC_DMAAccessMode = ADC_DMAAccessMode_1; // 2 half-words one by one, 1 then 2
  ADC_CommonInitStructure.ADC_TwoSamplingDelay = ADC_TwoSamplingDelay_5Cycles;
  ADC_CommonInit(&ADC_CommonInitStructure);
 
  ADC_InitStructure.ADC_Resolution = ADC_Resolution_12b;
  ADC_InitStructure.ADC_ScanConvMode = DISABLE; // 1 Channel
  ADC_InitStructure.ADC_ContinuousConvMode = DISABLE; // Conversions Triggered
  ADC_InitStructure.ADC_ExternalTrigConvEdge = ADC_ExternalTrigConvEdge_Rising;
  ADC_InitStructure.ADC_ExternalTrigConv = ADC_ExternalTrigConv_T2_TRGO;
  ADC_InitStructure.ADC_DataAlign = ADC_DataAlign_Right;
  ADC_InitStructure.ADC_NbrOfConversion = 1;
  ADC_Init(ADC1, &ADC_InitStructure);
  ADC_Init(ADC2, &ADC_InitStructure); // Mirror on ADC2
 
  /* ADC1 regular channel 10 configuration */
  ADC_RegularChannelConfig(ADC1, ADC_Channel_10, 1, ADC_SampleTime_15Cycles); // PC0
     
  /* ADC2 regular channel 11 configuration */
  ADC_RegularChannelConfig(ADC2, ADC_Channel_11, 1, ADC_SampleTime_15Cycles); // PC1
 
  /* Enable DMA request after last transfer (Multi-ADC mode)  */
  ADC_MultiModeDMARequestAfterLastTransferCmd(ENABLE);
 
  /* Enable ADC1 */
  ADC_Cmd(ADC1, ENABLE);
 
  /* Enable ADC2 */
  ADC_Cmd(ADC2, ENABLE);
}
 
/**************************************************************************************/
 
__IO uint16_t ADCDualConvertedValues[DATA_SIZE*2*DOWN_SAMPLE]; // Filled as pairs ADC1, ADC2
 
static void DMA_Configuration(void)
{
  DMA_InitTypeDef DMA_InitStructure;
 
  DMA_InitStructure.DMA_Channel = DMA_Channel_0;
  DMA_InitStructure.DMA_Memory0BaseAddr = (uint32_t)&ADCDualConvertedValues;
  DMA_InitStructure.DMA_PeripheralBaseAddr = (uint32_t)0x40012308; // CDR_ADDRESS; Packed ADC1, ADC2
  DMA_InitStructure.DMA_DIR = DMA_DIR_PeripheralToMemory;
  DMA_InitStructure.DMA_BufferSize = DATA_SIZE*2*DOWN_SAMPLE; // Count of 16-bit words
  DMA_InitStructure.DMA_PeripheralInc = DMA_PeripheralInc_Disable;
  DMA_InitStructure.DMA_MemoryInc = DMA_MemoryInc_Enable;
  DMA_InitStructure.DMA_PeripheralDataSize = DMA_PeripheralDataSize_HalfWord;
  DMA_InitStructure.DMA_MemoryDataSize = DMA_MemoryDataSize_HalfWord;
  DMA_InitStructure.DMA_Mode = DMA_Mode_Circular;
  DMA_InitStructure.DMA_Priority = DMA_Priority_High;
  DMA_InitStructure.DMA_FIFOMode = DMA_FIFOMode_Enable;
  DMA_InitStructure.DMA_FIFOThreshold = DMA_FIFOThreshold_HalfFull;
  DMA_InitStructure.DMA_MemoryBurst = DMA_MemoryBurst_Single;
  DMA_InitStructure.DMA_PeripheralBurst = DMA_PeripheralBurst_Single;
  DMA_Init(DMA2_Stream0, &DMA_InitStructure);
 
  /* Enable DMA Stream Half / Transfer Complete interrupt */
  DMA_ITConfig(DMA2_Stream0, DMA_IT_TC | DMA_IT_HT, ENABLE);
 
  /* DMA2_Stream0 enable */
  DMA_Cmd(DMA2_Stream0, ENABLE);
}
 
/**************************************************************************************/
 
void TIM2_Configuration(void)
{
  TIM_TimeBaseInitTypeDef TIM_TimeBaseStructure;
 
  /* Time base configuration */
  TIM_TimeBaseStructInit(&TIM_TimeBaseStructure);
  TIM_TimeBaseStructure.TIM_Period = 84000000/(3840*DOWN_SAMPLE)-1; // 3.6 KHz, from 84 MHz TIM2CLK (ie APB1 = HCLK/4, TIM2CLK = HCLK/2)
  TIM_TimeBaseStructure.TIM_Prescaler = 0;
  TIM_TimeBaseStructure.TIM_ClockDivision =  TIM_CKD_DIV1;
  TIM_TimeBaseStructure.TIM_CounterMode = TIM_CounterMode_Up;
  TIM_TimeBaseInit(TIM2, &TIM_TimeBaseStructure);
 
  /* TIM2 TRGO selection */
  TIM_SelectOutputTrigger(TIM2, TIM_TRGOSource_Update); // ADC_ExternalTrigConv_T2_TRGO
 
  /* TIM2 enable counter */
  TIM_Cmd(TIM2, ENABLE);
}
 
/**************************************************************************************/
 
void NVIC_Configuration(void)
{
  NVIC_InitTypeDef NVIC_InitStructure;
 
  /* Enable the DMA Stream IRQ Channel */
  NVIC_InitStructure.NVIC_IRQChannel = DMA2_Stream0_IRQn;
  NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 0;
  NVIC_InitStructure.NVIC_IRQChannelSubPriority = 0;
  NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
  NVIC_Init(&NVIC_InitStructure);
}
 
 
/**************************************************************************************/		

void DMA2_Stream0_IRQHandler(void)
{
	int i;
	int j;
	float data_conv = 3.3/4096;
	float offset = (float)5*22/(47+22);
	float v_zoom = 510*120/20/8.88*(110*sqrt(2))/225;
	float c_zoom = 100/0.05/18/2;
	float v_tol = 0.261;
	float c_tol = 0.1718;
	//float v_tol_0 = 9.5*(120*sqrt(2))/225;
	//float c_tol_0 = 9.5;

	/* Test on DMA Stream Half Transfer interrupt */
  if(DMA_GetITStatus(DMA2_Stream0, DMA_IT_HTIF0))
  {
    /* Clear DMA Stream Half Transfer interrupt pending bit */
    DMA_ClearITPendingBit(DMA2_Stream0, DMA_IT_HTIF0);
		//t0= TIM_GetCounter(TIM3)+(u32)timeout*65536;
		for(i=0;i<DATA_SIZE/2;i++)
		{
			for(j=0;j<DOWN_SAMPLE;j++)
			{
				if(j == 0)
				{
					Data_v[i]=ADCDualConvertedValues[2*i*DOWN_SAMPLE+2*j];			
					Data_c[i]=ADCDualConvertedValues[2*i*DOWN_SAMPLE+2*j+1];
				}
				else
				{
					Data_v[i]=Data_v[i]+ADCDualConvertedValues[2*i*DOWN_SAMPLE+2*j];
					Data_c[i]=Data_c[i]+ADCDualConvertedValues[2*i*DOWN_SAMPLE+2*j+1];
				}
			}
			Data_v[i]=((Data_v[i]/DOWN_SAMPLE)*data_conv-offset-v_tol)*v_zoom;
			Data_c[i]=((Data_c[i]/DOWN_SAMPLE)*data_conv-offset-c_tol)*c_zoom;
			//t0= TIM_GetCounter(TIM3)+(u32)timeout*65536;
				
			// Add code here to process first half of buffer (ping)
		}
		//HalfDataReady = 1;
  }
	
  /* Test on DMA Stream Transfer Complete interrupt */
  if(DMA_GetITStatus(DMA2_Stream0, DMA_IT_TCIF0))
  {
    /* Clear DMA Stream Transfer Complete interrupt pending bit */
    DMA_ClearITPendingBit(DMA2_Stream0, DMA_IT_TCIF0);
		for(i=DATA_SIZE/2;i<DATA_SIZE;i++)
		{
			for(j=0;j<DOWN_SAMPLE;j++)
			{
				if(j == 0)
				{
					Data_v[i]=ADCDualConvertedValues[2*i*DOWN_SAMPLE+2*j];			
					Data_c[i]=ADCDualConvertedValues[2*i*DOWN_SAMPLE+2*j+1];
				}
				else
				{
					Data_v[i]=Data_v[i]+ADCDualConvertedValues[2*i*DOWN_SAMPLE+2*j];
					Data_c[i]=Data_c[i]+ADCDualConvertedValues[2*i*DOWN_SAMPLE+2*j+1];
				}
			}
			Data_v[i]=((Data_v[i]/DOWN_SAMPLE)*data_conv-offset-v_tol)*v_zoom;
			Data_c[i]=((Data_c[i]/DOWN_SAMPLE)*data_conv-offset-c_tol)*c_zoom;
			//t0= TIM_GetCounter(TIM3)+(u32)timeout*65536;
				
			// Add code here to process first half of buffer (ping)
			// Add code here to process second half of buffer (pong)
			//t0= TIM_GetCounter(TIM3)+(u32)timeout*65536;
			
		}
		DataReady = 1;
  }
}

