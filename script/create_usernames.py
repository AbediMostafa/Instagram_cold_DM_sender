from openai import OpenAI

# ایجاد یک نمونه از کلاینت با کلید API خود
client = OpenAI(base_url='https://api.gapgpt.app/v1', api_key='sk-yj80RwM9eGAAbnLfYvp584qn9g2rqkbHR8ZkdAzeVL4RjK50')

content = '''
you are a instagram name,username maker
the name,username pairs should be iranian and man name,usernames
the length of usernames should vary(long, short and medium) and unique
the format should be like this :
farbod_ak4__r,فربد اکرم
first instagram username and a full name seperated with,
first name and family name should be mixed in username ( you can use first name first and sometimes family name first)
in username you can use numbers, _ and __ signs in the middle, first and last but follow the instagram username rules
so the format sometimes would be like this:
mhmd.92_rez_a,محمد رضایی
mi__lanarash_,آرش میلانی
pouy.an_kh4_r,پویان خلیل‌پور
sometimes first name comes first in the username and sometimes last name comes first,
please combine first name, last name digits and _ signs to completely make different usernames
sometimes you may want to dont include last name in the username like this:
shahi1n__84,شاهین اکبری
which is ok,
sometimes you may use like this:
sometimes you may last name come first like this:
bhshti.rez1a_,رضا بهشتی  
and so on, please give me 100 full name, username mix like this for me without asking anything
dont include the line number or anything extra, just fullname and username in each row

'''
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": content}
    ]
)

print(response.choices[0].message.content)
print(response.choices)
