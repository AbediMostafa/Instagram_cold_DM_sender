import asyncio
import aiohttp

mobile_ids = ['ONtJb']
# mobile_ids = ['ONtJb', 'ZURe1', 'kZYvS', 'gcsTe', '73UsF']

URL = 'https://openapi.duoplus.net/api/v1/cloudPhone/command'
HEADERS = {
    'DuoPlus-API-Key': '288e0cbe-2e1f-491b-a4d2-424c396d229a',
    'Content-Type': 'application/json'
}


async def send_command(session, mobile_id, command):
    payload = {
        'image_ids': [mobile_id],
        'command': command
    }

    try:
        async with session.post(
            URL,
            headers=HEADERS,
            json=payload,
            ssl=False
        ) as response:

            data = await response.json()

            print(
                f'[{mobile_id}] '
                f'{command} -> '
                f'{response.status}: {data}'
            )

            return data

    except Exception as e:
        print(
            f'[{mobile_id}] '
            f'{command} ERROR: {e}'
        )

        return None

async def main():
    async with aiohttp.ClientSession() as session:

        tasks = []

        for i in range(13):
            for mobile_id in mobile_ids:

                # Swipe request
                tasks.append(
                    asyncio.create_task(
                        send_command(
                            session,
                            mobile_id,
                            'input swipe 540 1400 540 374 250'
                        )
                    )
                )

                # Dumpsys request
                tasks.append(
                    asyncio.create_task(
                        send_command(
                            session,
                            mobile_id,
                            'dumpsys window | grep mCurrentFocus'
                        )
                    )
                )

        # Wait until ALL requests have completed
        results = await asyncio.gather(*tasks)

        print(f'\nCompleted {len(results)} requests.')


if __name__ == '__main__':
    asyncio.run(main())