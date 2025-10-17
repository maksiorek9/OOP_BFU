namespace lab1;
/*
  Создать класс AngleRange для хранения промежтка для углов
 - Реализовать механизм создания объекта через задание начальной и конечной точки промежукта в виде углов float, int или Angle+
 - Предусмотреть возможность использования включающих и исключающих промежутков+
 - реализовать возможность сравнения объектов на эквивалентность (eq)+
 - реализовать строкове представление объекта (str, repr)+
 - реализовать получение длины промежутка (abs или отдельны метод)+
 - реализовать сравнение промежутков+
 - реализовать операцию in для проверки входит один промежуток в другой или угол в промежуток+
 - реализовать операции сложения, вычитания(результат в общем виде - список промежутков)+

 */
public class AngelRange
{
    Angel[] angels = new Angel[2];
    public float leght ;
    public string str_angel = "";
    public AngelRange(Angel start, Angel end, string IN ="")
    {
        str_angel = $"{start}; {end}";
        if (IN == "[]")
        {
            angels[0] = new Angel(start.radian + 1);
            angels[1] = new Angel(end.radian + 1);
            str_angel = "[" + str_angel + "]";
            leght =float.Abs( start.radian) - float.Abs( end.radian);
            return;
        }

        else
        {
            angels[0] = start;
            angels[1] = end;
            str_angel = "(" + str_angel + ")";
            leght =float.Abs( angels[0].radian) - float.Abs( angels[1].radian);
        }
    }

    public static bool operator==(AngelRange a, AngelRange b)
    {
        return a.leght == b.leght;
    }

    public static bool operator !=(AngelRange a, AngelRange b)
    {
        return a.leght != b.leght;
    }

    public static bool operator >(AngelRange a, AngelRange b)
    {
        return a.leght < b.leght;
    }

    public static bool operator <(AngelRange a, AngelRange b)
    {
        return a.leght < b.leght;
    }

    public static float operator +(AngelRange a, AngelRange b)
    {
        return a.leght + b.leght;
    }
    public static float operator -(AngelRange a, AngelRange b)
    {
        return a.leght - b.leght;
    }


    public bool IN(AngelRange a, AngelRange b)
    {
        var firsA = a.angels[0];
        var secondA = a.angels[1]; 
        var firsB = b.angels[0];
        var secondB = b.angels[1];
        if (firsA >= firsB && secondA <= secondB)
            return true;
        return false;
    }

    
}