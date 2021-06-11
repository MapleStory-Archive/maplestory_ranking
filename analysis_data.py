import json
import csv

class_occ_data = {}
server_occ_data = {}
guild_occ_data = {}
for page_index in range(21):
    with open(f'./rank/maplestory_rank_page_{page_index}.json', 'r', encoding='utf-8') as data_file:
        data = json.load(data_file)
        for i in range(len(data)):
            # # 직업 점유율
            if data[i]['class'] in class_occ_data.keys():
                class_occ_data[data[i]['class']] += 1
            else:
                class_occ_data[data[i]['class']] = 1

            # # 서버 점유율
            if data[i]['server'] in server_occ_data.keys():
                server_occ_data[data[i]['server']] += 1
            else:
                server_occ_data[data[i]['server']] = 1
            
            # 길드 점유율
            if data[i]['guild'] in guild_occ_data.keys():
                guild_occ_data[data[i]['guild']] += 1
            else:
                guild_occ_data[data[i]['guild']] = 1


# temp = 0
# with open('./guild_occ.csv', 'w', encoding='utf-8', newline='') as f:
#     for guild, occ in sorted(guild_occ_data.items(), key=lambda x: x[1], reverse=True):
#         csv.writer(f).writerow([temp, guild, occ])
#         temp += 1
#         if temp > 30: break

# temp = 0
# with open('./class_occ.csv', 'w', encodig='utf-8', newline='') as f:
#     for class, occ in sorted(class_occ_data.items(), key=lambda x: x[1], reverse=True):
#         csv.writer(f).writerow([temp, class, occ])
#         temp += 1

# temp = 0
# with open('./server_occ.csv', 'w', encoding='utf-8', newline='') as f:
#     for server, occ in sorted(server_occ_data.items(), key=lambda x: x[1], reverse=True):
#         csv.writer(f).writerow([temp, server, occ])
#         temp += 1

temp = 0
with open('./class_occ.csv', 'w', newline='', encoding='utf-8') as f:
    for classn, occ in sorted(class_occ_data.items(), key=lambda x: x[1], reverse=True):
        csv.writer(f).writerow([temp, classn, occ])
        temp += 1