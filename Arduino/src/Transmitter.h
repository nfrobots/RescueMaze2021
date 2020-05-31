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


template<typename I, typename C>
class TrParser
{
public:
	TrParser(I& interface, C callable, String head, String foot)
     : callable(callable), interface(interface), head(head), foot(foot) {}

	template<typename T>
	void operator()(const TrValue<T>& trvalue)
	{
		interface.print(callable(trvalue.name, trvalue.ref));
	}

	C callable;
    I& interface;
    String head, foot;
};

template<typename P, typename I, typename ... Ts>
class JsonTransmitter
{
public:
	JsonTransmitter(I& interface, P parser, const Ts& ... args) 
        : parser(parser), interface(interface), attrb(args...) {}

	void transmitt()
	{
        interface.print(parser.head);
		apply(parser, attrb);
        interface.print(parser.foot);
	}

public:
	P parser;
    I& interface;
	Tuple<Ts...> attrb;
};