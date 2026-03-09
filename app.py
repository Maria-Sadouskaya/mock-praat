"""
🎤 Анализатор интонации для студентов-лингвистов
Основан на Praat (метод Filtered Autocorrelation)
"""

"""
🎤 Анализатор интонации для студентов-лингвистов
Основан на Praat (метод Filtered Autocorrelation)
"""

import streamlit as st
import parselmouth
import matplotlib.pyplot as plt
import numpy as np
import tempfile
import os
from datetime import datetime
import pandas as pd
import subprocess
import sys

# Проверяем наличие FFmpeg и устанавливаем если нужно
try:
    subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
except:
    st.warning("⚠️ Устанавливаю FFmpeg...")
    if sys.platform == 'linux':
        os.system('apt-get update && apt-get install -y ffmpeg')
# Настройка страницы
st.set_page_config(
    page_title="Анализатор интонации",
    page_icon="🎤",
    layout="wide"
)

# Стили
st.markdown("""
<style>
    .stApp {
        background-color: #f5f5f5;
    }
    .main-title {
        text-align: center;
        color: #2c3e50;
        padding: 1.5rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-title h1 {
        color: white;
        margin: 0;
    }
    .main-title p {
        color: #e0e0e0;
        margin: 0.5rem 0 0 0;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #3498db;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Заголовок
st.markdown("""
<div class="main-title">
    <h1>🎤 Анализатор интонации</h1>
    <p>Для студентов-лингвистов • Основан на Praat (Filtered Autocorrelation)</p>
</div>
""", unsafe_allow_html=True)

# Боковая панель с настройками
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Praat_icon.png/120px-Praat_icon.png", width=80)
    st.header("⚙️ Настройки анализа")
    
    st.markdown("---")
    
    # Пресеты для разных голосов
    preset = st.selectbox(
        "🎯 Пресет голоса",
        ["Мужской", "Женский", "Ребенок", "Свой"]
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if preset == "Мужской":
            pitch_floor = st.number_input("Pitch floor (Гц)", 40, 150, 75)
            pitch_ceiling = st.number_input("Pitch ceiling (Гц)", 200, 400, 250)
        elif preset == "Женский":
            pitch_floor = st.number_input("Pitch floor (Гц)", 80, 200, 100)
            pitch_ceiling = st.number_input("Pitch ceiling (Гц)", 400, 800, 600)
        elif preset == "Ребенок":
            pitch_floor = st.number_input("Pitch floor (Гц)", 150, 250, 180)
            pitch_ceiling = st.number_input("Pitch ceiling (Гц)", 600, 1200, 800)
        else:
            pitch_floor = st.number_input("Pitch floor (Гц)", 40, 250, 75)
            pitch_ceiling = st.number_input("Pitch ceiling (Гц)", 200, 1200, 600)
    
    with col2:
        st.markdown("### ℹ️ Рекомендации")
        st.markdown("""
        - **Мужской:** 75-250 Hz
        - **Женский:** 100-600 Hz
        - **Ребенок:** 180-800 Hz
        """)
    
    st.markdown("---")
    
    # Дополнительные настройки
    st.markdown("### 📊 Дополнительно")
    show_spectrogram = st.checkbox("Показать спектрограмму", value=True)
    
    time_step = st.slider(
        "Временной шаг (мс)",
        5, 50, 10,
        help="Шаг анализа в миллисекундах"
    ) / 1000

# Основной интерфейс
tab1, tab2, tab3 = st.tabs(["🎤 Запись", "📁 Загрузка", "📚 Инструкция"])

# Вкладка 1: Запись с микрофона
with tab1:
    st.markdown("### 🎤 Запись с микрофона")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        audio_bytes = st.audio_input(
            "Нажмите для записи",
            key="recorder"
        )
        
        if audio_bytes:
            st.success("✅ Запись готова!")
            st.audio(audio_bytes)
            
            # Кнопка анализа
            if st.button("🔬 Анализировать запись", type="primary", use_container_width=True):
                with st.spinner("Анализирую..."):
                    # Сохраняем во временный файл
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                        tmp_file.write(audio_bytes.getvalue())
                        audio_path = tmp_file.name
                    
                    # Запускаем анализ
                    analyze_audio(audio_path, pitch_floor, pitch_ceiling, 
                                 time_step, show_spectrogram)
    
    with col2:
        st.markdown("""
        <div class="info-box">
        <h4>💡 Советы для записи:</h4>
        <ul>
            <li>Говорите в нормальном темпе</li>
            <li>Держите микрофон на расстоянии 10-15 см</li>
            <li>Избегайте фонового шума</li>
            <li>Произнесите фразу целиком</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

# Вкладка 2: Загрузка файла
with tab2:
    st.markdown("### 📁 Загрузить аудиофайл")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Выберите файл",
            type=['wav', 'mp3', 'mp4', 'm4a', 'ogg', 'webm'],
            help="Поддерживаются все популярные аудиоформаты"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ Загружен: {uploaded_file.name}")
            st.audio(uploaded_file)
            
            # Показываем информацию о файле
            file_size = len(uploaded_file.getvalue()) / 1024 / 1024
            st.caption(f"Размер: {file_size:.2f} MB")
            
            # Кнопка анализа
            if st.button("🔬 Анализировать файл", type="primary", use_container_width=True):
                with st.spinner("Анализирую..."):
                    # Сохраняем во временный файл
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        audio_path = tmp_file.name
                    
                    # Запускаем анализ
                    analyze_audio(audio_path, pitch_floor, pitch_ceiling,
                                 time_step, show_spectrogram)
    
    with col2:
        st.markdown("""
        <div class="info-box">
        <h4>📌 Поддерживаемые форматы:</h4>
        <ul>
            <li>WAV (рекомендуется)</li>
            <li>MP3</li>
            <li>MP4/M4A</li>
            <li>OGG</li>
            <li>WebM</li>
        </ul>
        <p>Файлы автоматически конвертируются в WAV</p>
        </div>
        """, unsafe_allow_html=True)

# Вкладка 3: Инструкция
with tab3:
    st.markdown("### 📚 Как пользоваться анализатором")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="success-box">
        <h4>📝 Пошаговая инструкция:</h4>
        <ol>
            <li><b>Выберите способ:</b> запись или загрузка файла</li>
            <li><b>Настройте параметры:</b> выберите пресет под ваш голос</li>
            <li><b>Запишите/загрузите</b> аудио</li>
            <li><b>Нажмите "Анализировать"</b></li>
            <li><b>Изучите результаты</b> и графики</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h4>🎯 Что анализируется:</h4>
        <ul>
            <li>Интонационный контур</li>
            <li>Статистика частоты</li>
            <li>Тип интонации</li>
            <li>Паузы в речи</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="warning-box">
        <h4>⚠️ Возможные проблемы:</h4>
        <ul>
            <li><b>Пик 577 Гц вместо 144 Гц</b> - уменьшите Pitch ceiling</li>
            <li><b>Нет графика</b> - говорите громче</li>
            <li><b>Шум на графике</b> - уберите фоновый шум</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h4>🔬 Метод:</h4>
        <p>Filtered Autocorrelation (как в Praat)</p>
        <p>Единицы: Гц (логарифмическая шкала)</p>
        </div>
        """, unsafe_allow_html=True)

# Функция анализа
def analyze_audio(audio_path, pitch_floor, pitch_ceiling, time_step, show_spectrogram):
    """Основная функция анализа"""
    
    try:
        # Загружаем звук
        sound = parselmouth.Sound(audio_path)
        
        # Анализ интонации
        pitch = sound.to_pitch(
            time_step=time_step,
            pitch_floor=pitch_floor,
            pitch_ceiling=pitch_ceiling
        )
        
        # Получаем данные
        pitch_values = pitch.selected_array['frequency']
        times = pitch.xs()
        
        # Статистика
        valid = pitch_values > 0
        clean_pitch = pitch_values[valid]
        clean_times = times[valid]
        
        if len(clean_pitch) == 0:
            st.error("❌ Голос не распознан. Попробуйте другие настройки или говорите громче.")
            return
        
        # Вычисляем статистику
        max_f0 = np.max(clean_pitch)
        min_f0 = np.min(clean_pitch)
        mean_f0 = np.mean(clean_pitch)
        median_f0 = np.median(clean_pitch)
        std_f0 = np.std(clean_pitch)
        max_time = clean_times[np.argmax(clean_pitch)]
        
        # Определяем количество пауз
        pauses = np.sum(pitch_values == 0)
        pause_percent = (pauses / len(pitch_values)) * 100
        
        # ========== РЕЗУЛЬТАТЫ ==========
        st.markdown("---")
        st.markdown("## 📊 Результаты анализа")
        
        # Метрики в колонках
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Максимум", f"{max_f0:.1f} Гц")
        with col2:
            st.metric("Минимум", f"{min_f0:.1f} Гц")
        with col3:
            st.metric("Среднее", f"{mean_f0:.1f} Гц")
        with col4:
            st.metric("Медиана", f"{median_f0:.1f} Гц")
        
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric("Стд. отклонение", f"{std_f0:.1f} Гц")
        with col6:
            st.metric("Паузы", f"{pauses} ({pause_percent:.0f}%)")
        with col7:
            st.metric("Длительность", f"{clean_times[-1]:.2f} сек")
        with col8:
            st.metric("Пик на", f"{max_time:.2f} сек")
        
        # ========== ГРАФИКИ ==========
        st.markdown("### 📈 Интонационный контур")
        
        # Создаем фигуру
        fig = plt.figure(figsize=(15, 8))
        
        # Интонационный контур
        ax1 = plt.subplot(2, 1, 1)
        
        # Показываем паузы как разрывы
        plot_pitch = pitch_values.copy()
        plot_pitch[plot_pitch == 0] = np.nan
        
        ax1.plot(times, plot_pitch, 'b-', linewidth=2, label='Интонация')
        ax1.plot(max_time, max_f0, 'ro', markersize=10, label=f'Пик: {max_f0:.1f} Гц')
        ax1.axhline(y=mean_f0, color='g', linestyle='--', alpha=0.7, linewidth=2, 
                   label=f'Среднее: {mean_f0:.1f} Гц')
        
        # Отмечаем паузы
        pause_times = times[pitch_values == 0]
        if len(pause_times) > 0:
            ax1.scatter(pause_times, [pitch_floor] * len(pause_times), 
                       color='red', marker='x', s=50, label='Паузы', alpha=0.5)
        
        ax1.set_xlabel('Время (секунды)')
        ax1.set_ylabel('Частота (Гц)')
        ax1.set_title('Интонационный контур (Filtered Autocorrelation)')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(pitch_floor, pitch_ceiling)
        ax1.legend(loc='upper right')
        
        # Статистика
        ax2 = plt.subplot(2, 1, 2)
        stats_data = ['Минимум', 'Среднее', 'Медиана', 'Максимум']
        stats_values = [min_f0, mean_f0, median_f0, max_f0]
        colors = ['green', 'blue', 'orange', 'red']
        
        bars = ax2.bar(stats_data, stats_values, color=colors, alpha=0.7)
        ax2.set_ylabel('Частота (Гц)')
        ax2.set_title('Статистика частоты')
        
        for bar, val in zip(bars, stats_values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.1f} Гц', ha='center', va='bottom')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        
        # Спектрограмма (опционально)
        if show_spectrogram:
            st.markdown("### 🎵 Спектрограмма")
            
            fig2, ax = plt.subplots(figsize=(15, 5))
            
            # Создаем спектрограмму
            spectrogram = sound.to_spectrogram(window_length=0.03, time_step=0.002)
            spectrogram_db = 10 * np.log10(spectrogram.values + 1e-10)
            
            # Ограничиваем частоту
            frequencies = spectrogram.y_grid()
            freq_limit_idx = np.argmin(np.abs(frequencies - 5000))
            
            im = ax.imshow(spectrogram_db[:freq_limit_idx, :], 
                     aspect='auto', origin='lower',
                     extent=[0, len(sound.values[0])/sound.sampling_frequency,
                            0, frequencies[freq_limit_idx-1]],
                     cmap='magma')
            
            # Накладываем интонацию
            ax.plot(times, pitch_values, 'c-', linewidth=2, alpha=0.8)
            
            ax.set_xlabel('Время (секунды)')
            ax.set_ylabel('Частота (Гц)')
            ax.set_title('Спектрограмма + интонационный контур')
            ax.set_ylim(0, 5000)
            
            plt.colorbar(im, label='Интенсивность (дБ)')
            st.pyplot(fig2)
            plt.close()
        
        # ========== АНАЛИЗ ИНТОНАЦИИ ==========
        st.markdown("### 💡 Интерпретация результатов")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🗣️ Характеристики голоса")
            
            # Определяем тип голоса
            if mean_f0 < 120:
                voice_type = "Низкий (бас/баритон)"
            elif mean_f0 < 165:
                voice_type = "Средний (тенор/альт)"
            elif mean_f0 < 220:
                voice_type = "Высокий (сопрано)"
            else:
                voice_type = "Очень высокий"
            
            st.write(f"**Тип голоса:** {voice_type}")
            
            # Вариативность
            if std_f0 < 20:
                variation = "Низкая (монотонная речь)"
            elif std_f0 < 40:
                variation = "Средняя (нормальная речь)"
            else:
                variation = "Высокая (эмоциональная речь)"
            
            st.write(f"**Вариативность:** {variation}")
        
        with col2:
            st.markdown("#### 🔍 Тип интонации")
            
            # Определяем тип интонации
            peak_position = max_time / clean_times[-1]
            
            if peak_position > 0.7 and (max_f0 - mean_f0) > 30:
                st.success("🔴 **ВОПРОСИТЕЛЬНАЯ ИНТОНАЦИЯ**")
                st.write(f"• Подъем: {max_f0 - mean_f0:.1f} Гц")
            
            elif std_f0 < 20:
                st.info("🔵 **МОНОТОННАЯ РЕЧЬ**")
            
            elif max_f0 - min_f0 > 100:
                st.warning("🟡 **ЭМОЦИОНАЛЬНАЯ РЕЧЬ**")
            
            else:
                st.info("🔵 **ПОВЕСТВОВАТЕЛЬНАЯ**")
        
        # Аудиоплеер
        st.markdown("### 👂 Прослушать запись")
        st.audio(audio_path)
        
    except Exception as e:
        st.error(f"❌ Ошибка при анализе: {str(e)}")

# Подвал
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🎓 Для студентов-лингвистов • Метод Filtered Autocorrelation (Praat) • Гц (логарифмическая шкала)</p>
</div>
""", unsafe_allow_html=True)
