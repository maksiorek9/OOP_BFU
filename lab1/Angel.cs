using System.Globalization;
using System.Linq.Expressions;

namespace lab1;
/*
 * Создать класс Angle для хранения углов+
 - хранить внутреннее состоние угла в радианах+
 - возможность создания угла в радианах и градусах+
 - реализовать присваивание и получение угла в раддианах и градусах+
 - реализовать сранение углов с учетом, что 2 Pi*N + x = x, где Pi=3.14.1529..., N-целое +
 - релизовать перобразование угла в строку, float, int, str+
 - реализовать сравнение углов+
 - +реализовать сложение (в том числе с float и int, считая, что они заданы в радианах), вычитание (считая, что они заданы в радианах), умножение и деление на число
 - реализовать строкове представление объекта (str, repr)+
 */
public class Angel
{
    private float Radian { get; set; }
    private float Degrees { get; set; }
    
    
    

    private const float Pi = 3.141529f;

    public Angel(float nomber , string radian )
    {

        
        

        if (nomber > 0)
        {
            this.Degrees = (180.0f * nomber) / Pi;
            this.Radian = nomber;
            return;
        }
        else
            throw new ArgumentException("неправильно заданы радианы");
    }
    public Angel(float nomber  )
    {

        if (nomber > 0)
        {
            this.Degrees = nomber;
            this.Radian = (nomber * Pi) / 180.0f;
            return;
        }
        throw new ArgumentException("неверный значение градусов");
    }
    

    
    
    

    public static bool operator >(Angel a, Angel b)
    {
        return a.Radian > b.Radian;
    }

    public static bool operator <(Angel a, Angel b)
    {
        return a.Radian < b.Radian;
    }
    
    public static bool operator >=(Angel a, Angel b)
    {
        return a.Radian >= b.Radian;
    }

    public static bool operator <=(Angel a, Angel b)
    {
        return a.Radian <= b.Radian;
    }
    public bool comparison(Angel angel, Angel otherAngel,string ctr, int? N = null) // изначально хотелось перегрузить <
    {
        if (N is not null)
        {
            float? first = angel.Radian * N * Pi;
            float? second = otherAngel.Radian * N * Pi;
            
            if (ctr.Equals("<")) 
                return first < second;
            else
                return first > second;
        }

        return ErrorEventArgs.Empty.Equals(N);

    }

    public static float operator +(Angel angel, float scalar)
    {
        return angel.Radian + scalar;
    }
    public static float operator -(Angel angel, float scalar)
    {
        return angel.Radian - scalar;
    }
    public static float operator *(Angel angel, float scalar)
    {
        return angel.Radian * scalar;
    }
    public static float operator /(Angel angel, float scalar)
    {
        return angel.Radian / scalar;
    }
    public static float operator +(Angel angel, Angel scalar)
    {
        return angel.Radian + scalar.Radian;
    }
    public static float operator -(Angel angel, Angel scalar)
    {
        return angel.Radian - scalar.Radian;
    }
    public static float operator *(Angel angel, Angel scalar)
    {
        return angel.Radian * scalar.Radian;
    }
    public static float operator /(Angel angel, Angel scalar)
    {
        return angel.Radian / scalar.Radian;
    }

    public static string Tostring(Angel angel)
    {
        return angel.Radian.ToString();
    }

    public static float Parse(Angel angel)
    {
        return angel.Degrees;
    }

}