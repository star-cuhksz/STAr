close all;clc;clear
load dataprocess;

temp1=22590+31;
temp2=23510;

figure
plot(dataprocess(temp1:temp2,2));
figure
plot(dataprocess(temp1:temp2,4));
figure
plot(dataprocess(temp1:temp2,6));
figure
plot(dataprocess(temp1:temp2,8));
figure
plot(dataprocess(temp1:temp2,10));
figure
plot(dataprocess(temp1:temp2,12));
figure
plot(dataprocess(temp1:temp2,14));
figure
plot(dataprocess(temp1:temp2,16));
figure
plot(dataprocess(temp1:temp2,18));
figure
plot(dataprocess(temp1:temp2,20));

figure
subplot(2,5,1)
plot(dataprocess(temp1:temp2,2));
title('Heading')
subplot(2,5,2)
plot(dataprocess(temp1:temp2,4));
title('Main sail boom angle')
subplot(2,5,3)
plot(dataprocess(temp1:temp2,6));
title('Main sail angle')
subplot(2,5,4)
plot(dataprocess(temp1:temp2,8));
title('Jib sail angle')
subplot(2,5,5)
plot(dataprocess(temp1:temp2,10));
title('Jib sail boom angle')
subplot(2,5,6)
plot(dataprocess(temp1:temp2,12));
title('Voltage/V')
subplot(2,5,7)
plot(dataprocess(temp1:temp2,14));
title('Current/mA')
subplot(2,5,8)
plot(dataprocess(temp1:temp2,16));
title('Wind directrion value')
subplot(2,5,9)
plot(dataprocess(temp1:temp2,18));
title('Jib sail angle - Main sail angle')
subplot(2,5,10)
plot(dataprocess(temp1:temp2,20));
title('Jib sail angle - Main sail boom angle')


