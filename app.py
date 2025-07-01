import streamlit as st
import pickle
from PIL import Image

# Настройки страницы
st.set_page_config(page_title="Грибной ИИ", layout="centered")
st.title("🍄 ИИ для определения съедобности гриба")

# Загрузка модели и энкодеров
with open("model.pkl", "rb") as f:
    model, encoders, features = pickle.load(f)

# Перевод названий признаков
feature_labels = {
    "odor": "Запах",
    "gill-size": "Размер пластинок",
    "spore-print-color": "Цвет спорового отпечатка",
    "gill-color": "Цвет пластинок",
    "ring-type": "Тип кольца",
    "population": "Плотность популяции"
}

# Перевод значений признаков
value_translations = {
    "odor": {
        'a': 'миндальный', 'l': 'анисовый', 'c': 'клёновый', 'y': 'рыбный',
        'f': 'гнилой', 'm': 'затхлый', 'n': 'без запаха', 'p': 'едкий', 's': 'пряный'
    },
    "gill-size": {'b': 'широкие', 'n': 'узкие'},
    "spore-print-color": {
        'k': 'чёрный', 'n': 'коричневый', 'b': 'бежевый', 'h': 'шоколадный',
        'r': 'зелёный', 'o': 'оранжевый', 'u': 'фиолетовый', 'w': 'белый', 'y': 'жёлтый'
    },
    "gill-color": {
        'k': 'чёрный', 'n': 'коричневый', 'b': 'бежевый', 'h': 'шоколадный',
        'g': 'серый', 'e': 'бежевый', 'w': 'белый', 'y': 'жёлтый', 'r': 'зелёный', 'p': 'розовый', 'u': 'фиолетовый',
        'o': 'оранжевый'
    },
    "ring-type": {
        'c': 'кольцо-клубок', 'e': 'висячее', 'f': 'вспышкообразное',
        'l': 'большое', 'n': 'нет', 'p': 'подвесное', 's': 'приземистое', 'z': 'морщинистое'
    },
    "population": {
        'a': 'изолированная', 'c': 'скученная', 'n': 'многочисленная',
        's': 'рассеянная', 'v': 'разнообразная', 'y': 'обильная'
    }
}

# Форма ввода признаков
st.subheader("🔍 Введите характеристики гриба")
user_input = {}
for feat in features:
    opts = list(encoders[feat].classes_)
    translated_opts = [f"{opt} — {value_translations[feat].get(opt, opt)}" for opt in opts]

    if feat == "spore-print-color":
        translated_opts.insert(0, "❌ Не указывать")

    selected = st.selectbox(feature_labels[feat], translated_opts)

    if feat == "spore-print-color" and selected == "❌ Не указывать":
        user_input[feat] = None
    else:
        user_input[feat] = selected.split(" — ")[0]

# Кнопка предсказания
if st.button("Предсказать"):
    try:
        input_vector = []
        for feat in features:
            val = user_input[feat]
            if val is None:
                # Значение по умолчанию, если не указано (можно изменить на другой символ)
                val = encoders[feat].classes_[0]
            if val not in encoders[feat].classes_:
                raise ValueError(f"Неизвестное значение '{val}' для признака {feat}")
            encoded = encoders[feat].transform([val])[0]
            input_vector.append(encoded)

        prediction = model.predict([input_vector])[0]
        result = encoders["class"].inverse_transform([prediction])[0]
        proba = model.predict_proba([input_vector])[0]
        confidence = max(proba) * 100

        if result == "e":
            st.success(f"✅ Гриб съедобный!\n\n💡 Уверенность модели: {confidence:.1f}%")
        else:
            st.error(f"☠️ Гриб ядовитый!\n\n⚠️ Уверенность модели: {confidence:.1f}%")

    except ValueError as e:
        st.warning(f"⚠️ Ошибка предсказания: {str(e)}")

# Раздел с описаниями признаков
st.markdown("---")
st.header("📖 Как распознать признаки гриба")

# Gill-size изображения
st.subheader("📏 Размер пластинок")
col1, col2 = st.columns(2)
with col1:
    st.image("images/gill_wide.jpg", caption="Широкие пластинки", use_container_width=True)
with col2:
    st.image("images/gill_narrow.jpg", caption="Узкие пластинки", use_container_width=True)

# Цвет пластинок
st.subheader("🎨 Цвет пластинок")
st.image("images/gill_color.jpg", caption="Пример фиолетового цвета пластинки", use_container_width=True)

# Тип кольца
st.subheader("🔘 Тип кольца")
st.image("images/ring_type.jpg", caption="Пример вспышкообразного кольца", use_container_width=True)

# Дополнительная информация
st.markdown("### 🧭 Как определять другие признаки гриба")

st.markdown("""
- **Запах (odor):** аккуратно разломите шляпку гриба и понюхайте. Признаки могут варьироваться от фруктового до остро-пряного. Некоторые запахи (анисовый, миндальный) приятны, другие — (рыбный, креозотовый) неприятны.
- **Цвет спорового отпечатка:** положите шляпку гриба пластинками вниз на белую бумагу, накройте стаканом и оставьте на ночь. Утром посмотрите на цвет отпечатка.
- **Плотность популяции:** оцените количество таких грибов поблизости. Растут ли они кучно или поодиночке? Это поможет указать правильную плотность.
""")

st.markdown("🔎 Советуем использовать хорошее освещение и при необходимости — лупу. Чем точнее данные, тем надёжнее предсказание.")
