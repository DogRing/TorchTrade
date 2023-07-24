# TorchTrade
2021.06.20 - 2022.05.30  
개인 프로젝트

소켓통신으로 실시간 호가를 시계열 분석  
분석한 결과를 기반으로 실시간 구매/판매


## Train folder
### data_lodaer.py
모델 학습을 위한 데이터 수집  
전의 분당 데이터를 수집, csv로 저장  

### Dll2.dll
목푯값 반환 라이브러리  
목표 수치 이상 변화한 변화량을 측정하여 반환  
> 목표 : 0.25%  
> 현재 종가가 10000원일 때  
> 3일 후 10025원이 넘으면 +3  
> 3일 후 9975원 아래로 가면 -3

### indicators.py
데이터를 지표 데이터로 변환  
지표: SMA, EMA, WMA, RSI, BB, Mmt, MACD, 이격도  
  
데이터를 표준화  
MinMax, Std, skMinMax, skStd, skRob

### train.ipynb
모델 학습 후  .pt 확장자로 저장  

### valid.ipynb
과거 데이터에 적용 후 최적의 파라미터 도출  
도출 된 파라미터에 따라 다른 종목의 데이터에 적용/비교  
  
---
## Trade
### bitsocket.py
거래소 서버와 소켓 연결 후 결과 반환  

### ttorch.py
시계열 모델 구현부, 데이터의 결과값 반환  

### caldle.py
데이터 수집/분석/매매 실행부
사전 데이터의 전처리 값, 엑세스키를 넣고 실행  

--------------------------------------------------
--------------------------------------------------
--------------------------------------------------
## SCI-Net 구조를 사용한 이유
당시 단변량 시계열 데이터 부분에서 SOTA 였기 때문에  
일반적인 LSTM과 다른 것도 사용해 봤지만, 확실히 더 나은 성능을 보여줬습니다. 

## 지표를 선정한 기준
지표간에 데이터가 의존성이 있는 경우가 많았기 때문에  
다양한 지표를 사용하는 경우 추가를 하였고  
중요하다고 생각하는 지표는 추가로 넣었습니다. 

## 바로 실행이 되지 않는 이유
분당 데이터를 묶음으로 바로 받아와도 현재 시간이랑 최대 3분 차이가 나기 때문에  
3분의 시간동안 실시간 데이터를 받고 묶음 데이터와 합쳐서 시작합니다. 

## 결과
장기간의 데이터가 있으면 좋았겠지만 실행 중 거래소 서버의 점검기간 등의 요인이 많아서 장기간 시행하진 못했습니다.  
그래도 하락장에서 수수료 방어정도는 성공하는 것으로 파악됩니다.  
시간의 여유가 생기게 된다면 외부요인의 대처방안과 새로운 모델로 시험해보고 싶습니다. 
