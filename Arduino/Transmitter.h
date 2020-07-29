#pragma once

#include "ASL/Tuple.h"

#include <Arduino.h>


/**
 * Class holding a reference to a value which is to be transmitted and a name for the value.
 * 
 * Param:
 *  name: name of the value
 *  ref: value to be transmitted.
 */

template<typename T>
class TrValue
{
public:
	TrValue(String name, T& ref) : name(name), ref(ref) {}

	String name;
	T& ref;
};

/**
 * Parser object used to transmitt TrValue.
 * 
 * Param:
 *  callable: actual parser callable class (lambda!) which takes a name as String and value as any type. It should return a String.
 *  interface: Class with .print() function taking single argument returned by callable. E.g. Serial
 *  head: callable class (lambda!) which is executed at the beginning of each transmittion
 *  foot: callable class (lambda!) which is executed at the end of eacht transmittion
 */

template<typename C, typename I, typename H, typename F>
class TrParser
{
public:
	TrParser(const C& callable, I& interface, const H& head, const F& foot) //can not pass interface as constant reference as print function may not be constant
     : callable(callable), interface(interface), head(head), foot(foot) {}

	template<typename T>
	void operator()(const TrValue<T>& trvalue) const
	{
		interface.print(callable(trvalue.name, trvalue.ref));
	}

	const C& callable;
    I& interface;
    const H& head;
    const F& foot;
};

/**
 * Default Json parser
 */
TrParser JSON_TR_PARSER_DEFAULT(
    [](const auto& name, const auto& value) {
        return "\t\"" + name + "\": " + value + ",\n";
    },
    Serial,
    [](){ return String("{\n"); },
    [](){ return String("\t\"time\": " + String(millis()) + "\n}\n"); }
);

/**
 * JsonTransmitter object used to transmitt data sucha as sensor values in (json) format.
 * Format can be customized.
 * 
 * Param:
 *  parser: TrParser such as JSON_TR_PARSER_DEFAULT
 *  args...: arbitrary amount of TrValues to be transmittted
 */

template<template<typename, typename, typename, typename> typename P,
    typename C, typename I, typename H, typename F, typename ... Ts>
class JsonTransmitter
{
public:
	JsonTransmitter(const P<C, I, H, F>& parser, const Ts& ... args)
        : parser(parser), interface(parser.interface), attrb(args...) {}

	void transmitt()
	{
        interface.print(parser.head());
		asl::apply(parser, attrb);
        interface.print(parser.foot());
	}

private:
	const P<C, I, H, F>& parser;
    I& interface;
	asl::Tuple<Ts...> attrb;
};
