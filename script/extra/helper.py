import os
from time import sleep
from pathlib import Path
from random import randint
from script.models.Lead import Lead
from script.extra.adapters.SettingAdapter import SettingAdapter


def pause(_min, _max):
    sleep(randint(_min, _max))


def test_accounts():
    from spintax import spin

    leads = Lead.select().where(Lead.id.in_([36979,23365,23366]))
    for lead in leads:
        lead.dm_text = spin(SettingAdapter.cold_dm_spintax())

    return leads


def get_post_path(template_path):
    project_path = Path(__file__).parent.parent.parent
    return os.path.join(project_path, 'backend', 'storage', 'app', 'public', template_path)


def image_manipulator(path):
    import numpy as np
    from skimage import io, util, transform, exposure
    from pathlib import Path
    import os

    # Load the image
    image = io.imread(path)

    noisy_image = util.random_noise(image, mode='gaussian', var=0.01)

    # Apply a slight rotation
    rotated_image = transform.rotate(noisy_image, angle=randint(1, 10), mode='wrap')

    # Adjust brightness and contrast
    adjusted_image = exposure.adjust_gamma(rotated_image, gamma=0.9)
    # adjusted_image = exposure.adjust_sigmoid(rotated_image)

    # Convert the image to uint8 (8-bit unsigned integer)
    adjusted_image_uint8 = (adjusted_image * 255).astype(np.uint8)

    # Save the manipulated image
    io.imsave('generated_image.jpg', adjusted_image_uint8)

    project_path = Path(__file__).parent.parent

    return os.path.join(project_path, 'generated_image.jpg')


def chat_ai(prompt, max_tokens=400, temperature=0.7, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0):
    from openai import OpenAI

    # Set your API key
    client = OpenAI(api_key='sk-proj-RFjezVfYCmUPTEkaYLYmT3BlbkFJJ0MUSFUcVXojWDFw0dm7')

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty)

        return response.choices[0].message.content
    except Exception as e:
        raise Exception(e)
