#pragma once

#include "ASL/Tuple.h"

#include <Arduino.h>


template<typename T>
class TrValue
{
public:
	TrValue(String name, T& ref) : name(name), ref(ref) {}

	String name;
	T& ref;
};

template<typename C, typename I>
class TrExtractor
{
public:
	TrExtractor(C callable, I& interface) : callable(callable), interface(interface) {}

	template<typename T>
	void operator()(const TrValue<T>& trvalue)
	{
		interface.print(callable(trvalue.name, trvalue.ref));
	}

private:
	C callable;
    I& interface;
};

template<typename P, typename I, typename ... Ts>
class JsonTransmitter
{
public:
	JsonTransmitter(P parser, I& interf, const Ts& ... args) 
        : extractor(parser, interf), interf(interf), attrb(args...) {}

	void transmitt()
	{
		apply(extractor, attrb);
	}

public:
	TrExtractor<P, I> extractor;
    I& interf;
	Tuple<Ts...> attrb;
};