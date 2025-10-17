using lab1;
/*Лабораторная работа 1 (углы)

Создать класс Angle для хранения углов
 - хранить внутреннее состоние угла в радианах
 - возможность создания угла в радианах и градусах
 - реализовать присваивание и получение угла в раддианах и градусах
 - реализовать сранение углов с учетом, что 2 Pi*N + x = x, где Pi=3.14.1529..., N-целое 
 - релизовать перобразование угла в строку, float, int, str
 - реализовать сравнение углов
 - реализовать сложение (в том числе с float и int, считая, что они заданы в радианах), вычитание (считая, что они заданы в радианах), умножение и деление на число
 - реализовать строкове представление объекта (str, repr)  

Создать класс AngleRange для хранения промежтка для углов
 - Реализовать механизм создания объекта через задание начальной и конечной точки промежукта в виде углов float, int или Angle
 - Предусмотреть возможность использования включающих и исключающих промежутков
 - реализовать возможность сравнения объектов на эквивалентность (eq)
 - реализовать строкове представление объекта (str, repr)  
 - реализовать получение длины промежутка (abs или отдельны метод)
 - реализовать сравнение промежутков
 - реализовать операцию in для проверки входит один промежуток в другой или угол в промежуток
 - реализовать операции сложения, вычитания  (результат в общем виде - список промежутков)

Продемонстировать работоспособность реализованных методов*/
internal class Program
{
    public static void Main(string[] args)
    {
        var ang1 = new Angel(degrees:40);
        var ang2 = new Angel(radian:0.5f);
        var ang3 = new Angel(degrees:170);
        var ang4 = new Angel(radian:0.9f);

        Console.WriteLine(ang1.comparison(ang1, ang2,"[]",3));
        Console.WriteLine(ang2>ang1);
        Console.WriteLine($"{ang1.str_angel} {ang1.str_angel.GetType()} /n {ang1.int_angel} {ang1.int_angel.GetType()} /n" +
                          $"{ang1.radian} {ang1.radian.GetType()}");
        Console.WriteLine($"+ {ang1 + ang2}");
        Console.WriteLine($"- {ang1 - ang2}");
        Console.WriteLine($"/ {ang1 / ang2}");
        Console.WriteLine($"* {ang1 * ang2}");
        
        
        Console.WriteLine("--------------");
        AngelRange firs = new(ang1, ang2 , "[]");
        AngelRange second = new(ang3, ang4 , "()");
    
        if(firs.Equals(second))     
            Console.WriteLine("equal");
        else
            Console.WriteLine("not equal");
        Console.WriteLine(firs.str_angel);
        Console.WriteLine(firs.leght);
        Console.WriteLine(firs<second);
        if(firs.IN(firs, second))
            Console.WriteLine("first in second");
        Console.WriteLine($"+ {firs + second}");
        Console.WriteLine($"- {firs - second}");
    }
}