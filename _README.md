# Sailboat Test Arena ([STAr](http://sailboat.oicp.io/STAr/))

<p align="center">
  <img src="docs/fig/icon.png" href="http://sailboat.oicp.io/STAr" alt="STAr"/>
</p>

Sailboat Test Arena ([STAr](http://sailboat.oicp.io/STAr/)) is a research project related to teleoperation and automation of sailboats, conducted by State Joint Engineering Lab on Robotics and Intelligent Manufacturing, The Chinese University of Hong Kong, Shenzhen. This repository contains its web server, serial server, and some data.

## STAr Architecture

### Overview

<p align="center">
  <img src="docs/fig/overview.jpg" width=70% alt="Overview"/>
</p>

STAr Architecture. The platform comprises of mini-sized sailboats, named miniSailBots and an arena including an $8 m \times 10 m$ pool with $0.3 m$ depth water, quasi controllable wind field, ceiling-installed cameras, and network server.

### Physical Environment

<p align="center">
  <img src="docs/fig/panoramic.jpg" width=90% alt="panoramic"/>
</p>

This is a panoramic view of STAr platform in reality.

#### miniSailBots

<p align="center">
  <img src="docs/fig/miniSailBotA.jpg" width=30% alt="miniSailBotA"/>
  <img src="docs/fig/miniSailBotB.jpg" width=30% alt="miniSailBotB"/>
</p>

The different type of miniSailBot robots.

#### Camera

<p align="center">
  <img src="docs/fig/stitching_big.jpg" width=80% alt="Camera"/>
</p>

The concept of multi-camera stitching framework. The goal is for robots localization in a large view. 

<p align="center">
  <img src="docs/fig/DataCollection.jpg" width=50% alt="Camera"/>
</p>

#### Wind Field

<p align="center">
  <img src="docs/fig/uniform.jpg" width="250" alt="Wind Field"/>
</p>

This is the wind condition in our STAr platform.

#### Web Server

<p align="center">
  <img src="docs/fig/internet_server.png" width=50% alt="Internet Server"/>
</p>

As you can see, the UI is shown when you login in our system.

### Experiment

<p align="center">
  <img src="docs/fig/RLExperiment.jpg" width=33% alt="RLExperiment"/>
  <img src="docs/fig/STArDRL.png" width=30% alt="STArDRL"/>
</p>

This is the RL demo, we implemented for navigation.

<p align="center">
  <img src="docs/fig/signal.png" width=90% alt="Camera"/>
</p>

The sensor and control data will be generated. Besides, you can download or retrive these data for forward purpose.

#### Result

see [Experiment.mp4](STAr/video/exp.mp4)

## Repo. Catalogue

* [STAr](STAr)                - main workshop directory.
* [develop](develop)          - test & develop directory.
* [docs](docs)                - some reference documents.
* [dataprocess](dataprocess)  - some processed data.
* [README.md](README.md)      - readme file.
* [Sailboat_Nomenclature.jpg](Sailboat_Nomenclature.jpg) - Retrieved from [实用帆船术语中英对照解析之帆船结构](http://chinasailing.com/article/show?id=337)

## License

TODO : say something, this is a public repo.

## Reference

* [International Regulations for Preventing Collisions at Sea](https://en.wikipedia.org/wiki/International_Regulations_for_Preventing_Collisions_at_Sea)
