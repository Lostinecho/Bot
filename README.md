说明
本程序实现的是在telegram平台上的英文自动问答机器人，是基于rasa-0.15.1版本及其支持的外部组件实现的。

会话管理使用的是rasa-core，

rasa的language为英文：
language: "en"
rasa的pipeline配置如下：
pipeline: "spacy_sklearn"


该聊天机器人是基于rasa_nlu 搭建的，
在终端中安装rasa_nlu的0.15.1版本


在telegram bot中与bot_father对话以获得自己的机器人，得到token后即可放入程序中使用
同时也将获取美股的API放入token（以上两个步骤都需注册才能获得自己专属的token）



数据中使用了四个公司的缩写作为测试（因为没有查找到其他更多美股的缩写，故暂用这四家公司）
数据结构：
  文本类型	      含义	   数量	举例
  greet，       打招呼，    8，hello
  deny,         否认,      4，no
  affirm，      确认,       4， yes
  thankyou，    感谢,       5，thanks
  price_search，搜索公司,    8, show me Apple's latest price
  introduce，   自我介绍，   3,I'm Tom
  goodbye，     再见，       8, good bye


参考网站：
https://iexcloud.io/ 提供获取美国股市的API
https://core.telegram.org/bots telegram bot的官方教学
