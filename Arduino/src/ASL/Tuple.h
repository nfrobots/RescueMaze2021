#pragma once

#include "types.h"
#include "Util.h"

template<asl::size_t Index, typename T>
class _Tuple_elem
{
public:
	_Tuple_elem(const T& value) : value(value) {}
	T& get() { return value; }
private:
	T value;
};

template<asl::size_t Index, typename ... Dummy> class _Rec_tuple_elem_gen {}; //base case

template<asl::size_t Index, typename T, typename ... Us>
class _Rec_tuple_elem_gen<Index, T, Us...> : public _Tuple_elem<Index, T>, public _Rec_tuple_elem_gen<Index + 1, Us...>
{
public:
	_Rec_tuple_elem_gen(const T& arg, const Us& ... args) : _Tuple_elem<Index, T>(arg), _Rec_tuple_elem_gen<Index + 1, Us...>(args...) {}
};

template<typename ... Ts>
class Tuple : public _Rec_tuple_elem_gen<0, Ts...>
{
public:
	Tuple(const Ts& ... args) : _Rec_tuple_elem_gen<0, Ts...>(args...) {}
};

template<asl::size_t Index, typename T, typename ... Us>
struct _Get_type
{
	using type = typename _Get_type<Index - 1, Us...>::type;
};

template<typename T, typename ... Us>
struct _Get_type<0, T, Us...>
{
	using type = T;
};

template<asl::size_t Index, typename ... Ts>
auto& get(Tuple<Ts...>& tuple)
{
	return tuple._Tuple_elem<Index, typename _Get_type<Index, Ts...>::type>::get();
}

template<typename ... Ts>
asl::size_t get_size(const Tuple<Ts...>&)
{
	return sizeof...(Ts);
}

template<asl::size_t Index = 0, typename C, typename ... Ts>
typename enable_if<Index >= sizeof...(Ts), void>::type apply(const C& callable, Tuple<Ts...>& tuple) {} //base case

template<asl::size_t Index = 0, typename C, typename ... Ts>
typename enable_if<Index < sizeof...(Ts), void>::type apply(const C& callable, Tuple<Ts...>& tuple)
{
	callable.operator()(get<Index>(tuple));
	apply<Index + 1, C, Ts...>(callable, tuple);
}