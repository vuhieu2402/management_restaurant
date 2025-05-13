import uuid
import json
import re
from django.conf import settings
from django.db import transaction
from .models import Conversation, Message, RecommendedDish, UserPreference
from home.models import Dish, Category
from openai import OpenAI

# Khởi tạo client OpenAI hoặc OpenRouter dựa vào cấu hình
def get_ai_client():
    """
    Khởi tạo client OpenAI hoặc OpenRouter dựa vào cấu hình
    """
    if getattr(settings, 'USE_OPENROUTER', False):
        # Sử dụng OpenRouter
        client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_API_BASE,
            default_headers={
                "HTTP-Referer": "https://restaurant-management-app.com",
                "X-Title": "Restaurant Management System"
            }
        )
        return client
    else:
        # Sử dụng OpenAI trực tiếp
        return OpenAI(api_key=settings.OPENAI_API_KEY)

# Lấy model AI đang được cấu hình
def get_ai_model():
    """
    Lấy model AI đang được cấu hình (OpenAI hoặc OpenRouter)
    """
    if getattr(settings, 'USE_OPENROUTER', False):
        return settings.OPENROUTER_MODEL
    else:
        return settings.OPENAI_MODEL

@transaction.atomic
def create_or_get_conversation(session_id=None, user=None):
    """
    Tạo cuộc trò chuyện mới hoặc lấy cuộc trò chuyện hiện có
    """
    if session_id:
        conversation, created = Conversation.objects.get_or_create(
            session_id=session_id,
            defaults={'user': user}
        )
        # Cập nhật user nếu chưa có
        if not conversation.user and user:
            conversation.user = user
            conversation.save()
    else:
        # Tạo session_id mới
        session_id = str(uuid.uuid4())
        conversation = Conversation.objects.create(
            session_id=session_id,
            user=user
        )
    
    return conversation

@transaction.atomic
def add_message(conversation, content, sender):
    """
    Thêm tin nhắn vào cuộc trò chuyện
    """
    message = Message.objects.create(
        conversation=conversation,
        content=content,
        sender=sender
    )
    return message

def get_conversation_context(conversation):
    """
    Lấy ngữ cảnh cuộc trò chuyện để cung cấp cho AI
    """
    # Lấy 10 tin nhắn gần đây nhất
    messages = conversation.messages.order_by('created_at')[:10]
    
    # Lấy sở thích người dùng đã được phát hiện
    preferences = conversation.preferences.all()
    
    # Lấy món ăn đã đề xuất
    recommendations = conversation.recommendations.all()
    
    # Tạo context để gửi cho AI
    context = {
        "conversation_history": [{"role": msg.sender, "content": msg.content} for msg in messages],
        "detected_preferences": [{"type": pref.preference_type, "value": pref.preference_value} for pref in preferences],
        "previous_recommendations": [{"dish_name": rec.dish.name, "accepted": rec.is_accepted} for rec in recommendations]
    }
    
    return context

def process_preference_detection(conversation, user_message):
    """
    Phát hiện sở thích của người dùng từ tin nhắn
    """
    prompt = f"""
    Phân tích tin nhắn người dùng sau và trích xuất sở thích ăn uống:
    "{user_message}"
    
    Trả về kết quả theo định dạng JSON với các trường sau:
    - preference_type: loại sở thích (food_type, taste, allergy, diet, spicy_level)
    - preference_value: giá trị của sở thích
    - confidence: độ tin cậy từ 0.0 đến 1.0
    
    Nếu không phát hiện được sở thích nào, trả về danh sách rỗng.
    """
    
    try:
        client = get_ai_client()
        model = get_ai_model()
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content
        # Tìm và trích xuất JSON từ kết quả
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            
            # Lưu sở thích đã phát hiện
            if isinstance(result, list):
                for pref in result:
                    if pref.get('confidence', 0) > 0.6:  # Chỉ lưu khi đủ tin cậy
                        UserPreference.objects.create(
                            conversation=conversation,
                            user=conversation.user,
                            preference_type=pref.get('preference_type'),
                            preference_value=pref.get('preference_value'),
                            confidence=pref.get('confidence', 0.7)
                        )
            elif isinstance(result, dict) and result.get('preference_type'):
                if result.get('confidence', 0) > 0.6:
                    UserPreference.objects.create(
                        conversation=conversation,
                        user=conversation.user,
                        preference_type=result.get('preference_type'),
                        preference_value=result.get('preference_value'),
                        confidence=result.get('confidence', 0.7)
                    )
    except Exception as e:
        print(f"Error in preference detection: {e}")

def get_dish_recommendations(conversation, user_message, max_recommendations=3):
    """
    Lấy đề xuất món ăn dựa trên tin nhắn của người dùng và ngữ cảnh hội thoại
    """
    # Lấy danh sách món ăn
    all_dishes = Dish.objects.all()
    all_categories = Category.objects.all()
    
    # Chuẩn bị dữ liệu món ăn để cung cấp cho AI
    dish_data = []
    for dish in all_dishes:
        dish_data.append({
            "id": dish.id,
            "name": dish.name,
            "description": dish.description,
            "price": float(dish.price),
            "category": dish.category.name,
            "in_stock": dish.in_stock
        })
    
    category_data = [{"id": cat.id, "name": cat.name} for cat in all_categories]
    
    # Lấy ngữ cảnh cuộc trò chuyện
    context = get_conversation_context(conversation)
    
    # Tạo prompt cho AI
    prompt = f"""
    Vai trò của bạn: Bạn là trợ lý nhà hàng AI có nhiệm vụ đề xuất món ăn phù hợp với sở thích của khách hàng.
    
    Yêu cầu nhiệm vụ:
    1. Phân tích tin nhắn của người dùng để hiểu nhu cầu
    2. Kết hợp với sở thích đã biết của người dùng
    3. Đề xuất tối đa {max_recommendations} món ăn phù hợp từ danh sách món có sẵn
    4. Giải thích ngắn gọn lý do đề xuất cho mỗi món
    5. Trả lời thân thiện, tự nhiên như người thật

    Tin nhắn người dùng: "{user_message}"
    
    Lịch sử hội thoại và sở thích:
    {json.dumps(context, ensure_ascii=False)}
    
    Danh sách món ăn có sẵn:
    {json.dumps(dish_data, ensure_ascii=False)}
    
    Danh sách danh mục món ăn:
    {json.dumps(category_data, ensure_ascii=False)}
    
    Trả về kết quả với 2 phần:
    1. Một JSON object đặt trong <recommendations></recommendations> chứa mảng các món ăn đề xuất, mỗi món gồm "dish_id" và "reasoning"
    2. Tin nhắn trả lời thân thiện cho người dùng ở ngoài tags
    """
    
    try:
        client = get_ai_client()
        model = get_ai_model()
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=1000
        )
        
        result_text = response.choices[0].message.content
        
        # Tách phần JSON chứa đề xuất
        recommendations_match = re.search(r'<recommendations>(.*?)</recommendations>', result_text, re.DOTALL)
        recommendations_json = []
        
        if recommendations_match:
            try:
                recommendations_json = json.loads(recommendations_match.group(1))
            except:
                # Nếu không parse được JSON, thử tìm lại với pattern khác
                json_match = re.search(r'\[(.*?)\]', recommendations_match.group(1), re.DOTALL)
                if json_match:
                    recommendations_json = json.loads(json_match.group(0))
        
        # Lấy phần tin nhắn (loại bỏ phần JSON)
        bot_message = re.sub(r'<recommendations>.*?</recommendations>', '', result_text, flags=re.DOTALL).strip()
        
        # Lưu các đề xuất vào cơ sở dữ liệu
        saved_recommendations = []
        for rec in recommendations_json:
            dish_id = rec.get('dish_id')
            reasoning = rec.get('reasoning', '')
            
            try:
                dish = Dish.objects.get(id=dish_id)
                recommendation = RecommendedDish.objects.create(
                    conversation=conversation,
                    dish=dish,
                    reasoning=reasoning
                )
                saved_recommendations.append(recommendation)
            except Dish.DoesNotExist:
                continue
        
        return bot_message, saved_recommendations
    
    except Exception as e:
        print(f"Error in recommendation generation: {e}")
        return "Xin lỗi, tôi đang gặp vấn đề kỹ thuật khi đề xuất món ăn. Bạn có thể cho tôi biết thêm về sở thích của bạn không?", []

@transaction.atomic
def process_chat_message(user_message, session_id=None, user=None):
    """
    Xử lý tin nhắn từ người dùng và tạo phản hồi
    """
    # Tạo hoặc lấy cuộc trò chuyện
    conversation = create_or_get_conversation(session_id, user)
    
    # Lưu tin nhắn người dùng
    add_message(conversation, user_message, 'user')
    
    # Phát hiện sở thích từ tin nhắn
    process_preference_detection(conversation, user_message)
    
    # Tạo phản hồi và đề xuất món ăn
    bot_message, recommendations = get_dish_recommendations(conversation, user_message)
    
    # Lưu tin nhắn bot
    add_message(conversation, bot_message, 'bot')
    
    # Trả về kết quả
    return {
        'message': bot_message,
        'session_id': conversation.session_id,
        'recommendations': recommendations
    }

def mark_recommendation_feedback(recommendation_id, accepted):
    """
    Đánh dấu phản hồi của người dùng về đề xuất
    """
    try:
        recommendation = RecommendedDish.objects.get(id=recommendation_id)
        recommendation.is_accepted = accepted
        recommendation.save()
        return True
    except RecommendedDish.DoesNotExist:
        return False 