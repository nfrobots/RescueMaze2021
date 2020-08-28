#pragma once

#include "Tuple.h"

namespace asl
{
    template <class T>
    class Vector
    {
    private:
        T *arr;
        int size;
        int capacity;

    public:
        Vector();
        Vector(int size);
        template<typename ... Us>
        Vector(Us ... values);
        ~Vector();

        Vector(const Vector &other);
        Vector(Vector &&other) noexcept;

        T &operator[](int index);
        Vector<T> &operator=(const Vector &other);
        Vector<T> &operator=(Vector &&other) noexcept;

        int getSize();
        int getMem();

        void append(T val);
    };

    template <class T>
    Vector<T>::Vector()
    {
        size = 0;
        capacity = 1;
        arr = new T[capacity];
    }

    template<typename T>
    template<typename ... Us>
    Vector<T>::Vector(Us ... values)
    {
        size = 0;
        capacity = sizeof...(Us);
        arr = new T[capacity];

        asl::Tuple<Us...> t(values...);
        asl::apply([this](auto& value){append(value);}, t);
    }

    template <class T>
    Vector<T>::Vector(int size)
        : size(size)
    {
        if (size == 0)
            capacity = 1;
        else
            capacity = size;
        arr = new T[capacity];
    }

    template <class T>
    Vector<T>::~Vector()
    {
        delete[] arr;
    }

    template <class T>
    Vector<T>::Vector(const Vector &other)
    {
        size = other.size;
        capacity = other.size;
        arr = new T[capacity];
        for (int i = 0; i < size; i++)
        {
            arr[i] = other.arr[i];
        }
    }

    template <class T>
    Vector<T>::Vector(Vector &&other) noexcept
    {
        size = other.size;
        capacity = other.capacity;
        arr = other.arr;
        other.arr = nullptr;
    }

    template <class T>
    T &Vector<T>::operator[](int index)
    {
        if (!(index >= capacity))
        {
            if (index >= size)
            {
                size = index + 1;
            }
            return arr[index];
        }
        else
        {
            capacity = index + 1;
            T *newArr = new T[capacity];
            for (int i = 0; i < size; i++)
            {
                newArr[i] = arr[i];
            }
            size = capacity;
            delete[] arr;
            arr = newArr;
            return arr[index];
        }
    }

    template <class T>
    Vector<T> &Vector<T>::operator=(const Vector &other)
    {
        if (this == &other)
            return *this;
        if (size != other.size)
        {
            size = other.size;
            capacity = other.size;
            delete[] arr;
            arr = new T[capacity];
        }
        for (int i = 0; i < size; i++)
        {
            arr[i] = other.arr[i];
        }
        return *this;
    }

    template <class T>
    Vector<T> &Vector<T>::operator=(Vector &&other) noexcept
    {
        if (this == &other)
            return *this;
        size = other.size;
        capacity = other.capacity;
        delete[] arr;
        arr = other.arr;
        other.arr = nullptr;
        return *this;
    }

    template <class T>
    int Vector<T>::getSize()
    {
        return size;
    }

    template <class T>
    int Vector<T>::getMem()
    {
        return capacity * sizeof(T) + sizeof(capacity) + sizeof(size);
    }

    template <class T>
    void Vector<T>::append(T val)
    {
        if (size >= capacity)
        {
            capacity *= 2;
            T *newArr = new T[capacity];
            for (int i = 0; i < size; i++)
            {
                newArr[i] = arr[i];
            }
            delete[] arr;
            arr = newArr;
        }
        arr[size] = val;
        size++;
    }
} // namespace asl