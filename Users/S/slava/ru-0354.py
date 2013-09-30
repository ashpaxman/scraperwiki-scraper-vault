import scraperwiki
import re
# Blank Python

ids="""5297
5298
5304
5179
5126
5269
5270
5281
5274
5205
5202
5197
5116
5102
5100
5244
5229
5162
237718
95333
68008
5253
13654
5288
5296
13627
13625
5275
5150
5159
5221
5214
5292
5290
5262
5299
5128
54837
203798
203793
91035
76773
183890
175220
137309
95254
5289
5276
5225
5152
147936
5198
5111
5101
5245
5230
124049
159539
5216
7083
5294
5146
5282
5273
5295
5127
88921
169912
146556
148676
125611
149284
162383
135668
5277
199178
198869
12953
5199
5271
5104
5093
5246
5151
5125
103215
177460
180017
170435
152948
162386
5153
5201
5272
5110
5247
5130
5293
5291
5119
88804
160001
22656
163599
5160
5222
12816
5250
5103
5129
177468
170438
151593
5120
12304
5112
170455
77356
177465
5248
163604
5161
5154
5249
5095
191122
132927
5121
5135
5105
179229
5155
5106
12961
5156
5305
108156
5139
5107
13623
5251
5183
5206
5283
5133
5114
5131
5108
5138
5113
5137
5141
5142
5147
232848
5136
5143
5134
5144
5132
5145
5140
5148
5284
58694
5124
82327
115765
113273
5207
5254
5123
63441
63443
99462
5220
85322
172451
5182
76764
114876
5261
5208
5315
5320
5313
5453
5311
5287
5314
5307
5309
5318
96040
134799
5285
5259
143663
18255
5215
5200
5286
5180
97179
193465
155263
5217
5212
19298
5181
113070
155265
19302
152696
5186
42331
19300
52178
5258
5317
5302
5301
5310
5319
5308
5300
5306
5312
5456
5278
5231
13731
5252
5226
5163
5187
5255
82050
5260
19306
152568
150813
165582
5164
32655
5192
5232
5165
5189
5227
5233
5238
5239
5240
5241
5242
5243
5166
5190
5234
5228
6872
243757
144674
142589
145121
133249
128623
149037
5263
5265
95949
97567
193850
82351
157020
177605
173599
155365
152678
242669
243838
244230
238932
238936
198955
199650
103608
5264
6888
6887
6978
5203
5235
5149
5204
232854
244232
27932
134853
243759
13629
5267
5191
5280
5279
5268
5266
158068
5167
5194
5168
5188
5236
5169
5196
5171
5172
5173
83371"""
id=1
for i in ids.split("\n"):
    i=i.strip()

    html=scraperwiki.scrape("http://www.gazprombank.ru/bitrix/components/lenvendo/map.element.list/templates/.default/ajax_request.php?pop_up=Y&element_id="+i+"&metro=&all_rus=Y")
    
    branch_name=re.findall(r'<div class=\\"title\\">(.+?)</div>',html, re.I|re.U)
    address=re.findall(r'<div class=\\"text-office\\">.+?<span>(.+?)</span>',html, re.I|re.U|re.S)

    data={'id':id, 'branch_id':i, 'branch_name':branch_name[0] if branch_name !=[] else '', 'address':address[0] if address!=[] else '', 'html':html}
    scraperwiki.sqlite.save(unique_keys=['id'], data=data, table_name="branch_info_1")
    id+=1
    #print branch_name, address, i
    #exit()

import scraperwiki
import re
# Blank Python

ids="""5297
5298
5304
5179
5126
5269
5270
5281
5274
5205
5202
5197
5116
5102
5100
5244
5229
5162
237718
95333
68008
5253
13654
5288
5296
13627
13625
5275
5150
5159
5221
5214
5292
5290
5262
5299
5128
54837
203798
203793
91035
76773
183890
175220
137309
95254
5289
5276
5225
5152
147936
5198
5111
5101
5245
5230
124049
159539
5216
7083
5294
5146
5282
5273
5295
5127
88921
169912
146556
148676
125611
149284
162383
135668
5277
199178
198869
12953
5199
5271
5104
5093
5246
5151
5125
103215
177460
180017
170435
152948
162386
5153
5201
5272
5110
5247
5130
5293
5291
5119
88804
160001
22656
163599
5160
5222
12816
5250
5103
5129
177468
170438
151593
5120
12304
5112
170455
77356
177465
5248
163604
5161
5154
5249
5095
191122
132927
5121
5135
5105
179229
5155
5106
12961
5156
5305
108156
5139
5107
13623
5251
5183
5206
5283
5133
5114
5131
5108
5138
5113
5137
5141
5142
5147
232848
5136
5143
5134
5144
5132
5145
5140
5148
5284
58694
5124
82327
115765
113273
5207
5254
5123
63441
63443
99462
5220
85322
172451
5182
76764
114876
5261
5208
5315
5320
5313
5453
5311
5287
5314
5307
5309
5318
96040
134799
5285
5259
143663
18255
5215
5200
5286
5180
97179
193465
155263
5217
5212
19298
5181
113070
155265
19302
152696
5186
42331
19300
52178
5258
5317
5302
5301
5310
5319
5308
5300
5306
5312
5456
5278
5231
13731
5252
5226
5163
5187
5255
82050
5260
19306
152568
150813
165582
5164
32655
5192
5232
5165
5189
5227
5233
5238
5239
5240
5241
5242
5243
5166
5190
5234
5228
6872
243757
144674
142589
145121
133249
128623
149037
5263
5265
95949
97567
193850
82351
157020
177605
173599
155365
152678
242669
243838
244230
238932
238936
198955
199650
103608
5264
6888
6887
6978
5203
5235
5149
5204
232854
244232
27932
134853
243759
13629
5267
5191
5280
5279
5268
5266
158068
5167
5194
5168
5188
5236
5169
5196
5171
5172
5173
83371"""
id=1
for i in ids.split("\n"):
    i=i.strip()

    html=scraperwiki.scrape("http://www.gazprombank.ru/bitrix/components/lenvendo/map.element.list/templates/.default/ajax_request.php?pop_up=Y&element_id="+i+"&metro=&all_rus=Y")
    
    branch_name=re.findall(r'<div class=\\"title\\">(.+?)</div>',html, re.I|re.U)
    address=re.findall(r'<div class=\\"text-office\\">.+?<span>(.+?)</span>',html, re.I|re.U|re.S)

    data={'id':id, 'branch_id':i, 'branch_name':branch_name[0] if branch_name !=[] else '', 'address':address[0] if address!=[] else '', 'html':html}
    scraperwiki.sqlite.save(unique_keys=['id'], data=data, table_name="branch_info_1")
    id+=1
    #print branch_name, address, i
    #exit()

