using System.Globalization;

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
    public float radian { get; set; }
    public float degrees { get; set; }
    
    
    

    private const float pi = 3.141529f;

    public Angel(float radian = 0, float degrees = 0)
    {

        if (degrees > 0)
        {
            this.degrees = degrees;
            this.radian = (degrees * pi) / 180.0f;
           
            int_angel = (int)this.radian;
            str_angel =  Convert.ToString(this.radian, CultureInfo.InvariantCulture);
            return;
        }

        if (radian > 0)
        {
            this.degrees = (180.0f * radian) / pi;
            this.radian = radian;
            int_angel = (int)this.radian;
            str_angel =  Convert.ToString(this.radian, CultureInfo.InvariantCulture);

        }
    }

    public Angel()
    {

    }

    public string str_angel = "";


    public int int_angel = 0;
    
    

    public static bool operator >(Angel a, Angel b)
    {
        return a.radian > b.radian;
    }

    public static bool operator <(Angel a, Angel b)
    {
        return a.radian < b.radian;
    }

    public bool comparison(Angel angel, Angel otherAngel,string ctr, int? N = null) // изначально хотелось перегрузить <
    {
        if (N != null)
        {
            float? first = angel.radian * N * pi;
            float? second = otherAngel.radian * N * pi;
            
            if (ctr == "<")
                return first < second;
            else
                return first > second;
        }

        return ErrorEventArgs.Empty.Equals(N);

    }

    public static float operator +(Angel angel, float scalar)
    {
        return angel.radian + scalar;
    }
    public static float operator -(Angel angel, float scalar)
    {
        return angel.radian - scalar;
    }
    public static float operator *(Angel angel, float scalar)
    {
        return angel.radian * scalar;
    }
    public static float operator /(Angel angel, float scalar)
    {
        return angel.radian / scalar;
    }


}