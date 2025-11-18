/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "usart.h"
#include "gpio.h"
#include <string.h>
#include <stdio.h>

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
/* Buffer for UART reception */
#define CMD_BUFFER_SIZE 256
static uint8_t cmd_buffer[CMD_BUFFER_SIZE];
static uint16_t cmd_index = 0;
static volatile uint8_t cmd_ready = 0;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
void parse_and_execute_command(const char* cmd);
void motor_control(uint16_t steps, uint8_t direction);
void led_control(uint8_t state);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USART2_UART_Init();
  /* USER CODE BEGIN 2 */
  /* Start receiving first byte */
  HAL_UART_Receive_IT(&huart2, &cmd_buffer[0], 1);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
    /* Process received command */
    if (cmd_ready) {
      parse_and_execute_command((const char*)cmd_buffer);
      cmd_index = 0;
      cmd_ready = 0;
      HAL_UART_Receive_IT(&huart2, &cmd_buffer[0], 1);
    }
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 16;
  RCC_OscInitStruct.PLL.PLLN = 336;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV4;
  RCC_OscInitStruct.PLL.PLLQ = 4;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

/* UART RxCplt callback - called when character received */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
  if (huart->Instance == USART2) {
    uint8_t byte = cmd_buffer[cmd_index];
    
    if (byte == '\n' || byte == '\r') {
      cmd_buffer[cmd_index] = '\0';
      cmd_ready = 1;
    } else if (cmd_index < CMD_BUFFER_SIZE - 1) {
      cmd_index++;
      HAL_UART_Receive_IT(&huart2, &cmd_buffer[cmd_index], 1);
    }
  }
}

/* Parse and execute received command */
void parse_and_execute_command(const char* cmd)
{
  if (strncmp(cmd, "motor:", 6) == 0) {
    uint16_t steps = 0;
    uint8_t direction = 0;
    int parsed = sscanf(cmd, "motor:%hu:%hhu", &steps, &direction);
    
    if (parsed == 2 && steps <= 10000 && direction <= 1) {
      motor_control(steps, direction);
    } else {
      HAL_UART_Transmit(&huart2, (uint8_t*)"[ERROR] Invalid motor parameters\r\n", 34, 100);
    }
  } 
  else if (strncmp(cmd, "led:", 4) == 0) {
    if (strcmp(cmd, "led:on") == 0) {
      led_control(1);
    } else if (strcmp(cmd, "led:off") == 0) {
      led_control(0);
    } else {
      HAL_UART_Transmit(&huart2, (uint8_t*)"[ERROR] LED: use led:on or led:off\r\n", 36, 100);
    }
  }
  else if (strlen(cmd) > 0) {
    HAL_UART_Transmit(&huart2, (uint8_t*)"[ERROR] Unknown command\r\n", 25, 100);
  }
}

/* Motor control - set direction and step */
void motor_control(uint16_t steps, uint8_t direction)
{
  /* Set direction (1 = forward, 0 = backward) */
  if (direction) {
    HAL_GPIO_WritePin(MOTOR_DIR_GPIO_Port, MOTOR_DIR_Pin, GPIO_PIN_SET);
  } else {
    HAL_GPIO_WritePin(MOTOR_DIR_GPIO_Port, MOTOR_DIR_Pin, GPIO_PIN_RESET);
  }
  
  /* Generate step pulses */
  for (uint16_t i = 0; i < steps; i++) {
    HAL_GPIO_WritePin(MOTOR_STEP_GPIO_Port, MOTOR_STEP_Pin, GPIO_PIN_SET);
    HAL_Delay(1);
    HAL_GPIO_WritePin(MOTOR_STEP_GPIO_Port, MOTOR_STEP_Pin, GPIO_PIN_RESET);
    HAL_Delay(1);
  }
  
  HAL_UART_Transmit(&huart2, (uint8_t*)"[OK] Motor executed\r\n", 21, 100);
}

/* LED control - turn on/off */
void led_control(uint8_t state)
{
  if (state) {
    HAL_GPIO_WritePin(LED_INDICATOR_GPIO_Port, LED_INDICATOR_Pin, GPIO_PIN_SET);
  } else {
    HAL_GPIO_WritePin(LED_INDICATOR_GPIO_Port, LED_INDICATOR_Pin, GPIO_PIN_RESET);
  }
  HAL_UART_Transmit(&huart2, (uint8_t*)"[OK] LED updated\r\n", 17, 100);
}

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
