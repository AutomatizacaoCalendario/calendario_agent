import dateparser
from datetime import datetime

def parse_date_from_text(text: str) -> str | None:
    """
    Converte uma string de linguagem natural em uma data no formato AAAA-MM-DD.    
    Returns: formated date | None.
    """
    if not text:
        return None

    try:        
        settings = {
            'PREFER_DATES_FROM': 'future', 
            'DATE_ORDER': 'DMY',
        }

        parsed_date = dateparser.parse(text, languages=['pt'], settings=settings)

        if parsed_date:
            return parsed_date.strftime('%Y-%m-%d')
        else:
            return None
    except Exception as e:
        print(f"Erro ao fazer o parse da data: {e}")
        return None
